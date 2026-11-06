"""Run the golden set and report the four metrics.

    python eval/run_eval.py --live                   # against the deployed API
    python eval/run_eval.py --live --no-reranker     # the comparison arm
    python eval/run_eval.py --replay                 # fixtures, no Azure
    python eval/run_eval.py --live --gate baselines/2026-11-08.json

--live calls the service: costs tokens, varies between runs, tells the truth.
--replay re-scores recorded answers: free, deterministic, runs on every PR so
metric *code* can change without a cloud round-trip.

--gate exits non-zero on a regression. That exit code is the point of this
file: a number nobody enforces quietly rots.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

EVAL_DIR = Path(__file__).parent
GOLDEN = EVAL_DIR / "golden" / "questions.yaml"
FIXTURES = EVAL_DIR / "fixtures"
REPORTS = EVAL_DIR / "reports"

# How far a metric may slip before the gate fails. Not zero: these move between
# runs even at temperature 0. Set each from the spread you observe across three
# real runs - a threshold tighter than the noise floor produces failures nobody
# trusts, and a pipeline nobody trusts gets switched off.
TOLERANCE = {
    "recall_at_5": 0.05,
    "share_fully_grounded": 0.05,
    "citation_support_rate": 0.05,
    "correct_abstention_rate": 0.10,
}


@dataclass
class Summary:
    """Everything worth comparing between two runs."""

    run_id: str
    mode: str
    use_reranker: bool
    n_questions: int
    metrics: dict[str, float] = field(default_factory=dict)
    cost: dict[str, float] = field(default_factory=dict)
    per_question: list[dict] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "use_reranker": self.use_reranker,
            "n_questions": self.n_questions,
            "metrics": self.metrics,
            "cost": self.cost,
            "per_question": self.per_question,
        }


def load_questions(path: Path = GOLDEN) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    questions = data["questions"]

    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate question ids in the golden set.")

    return questions


def run_live(questions: list[dict], *, api_url: str, use_reranker: bool) -> Summary:
    """POST each question to the deployed API and score the responses.

    TODO Sun PM: POST {question, use_reranker} to {api_url}/ask, record each
    response to fixtures/ for replay, score through the four metrics, and
    aggregate. Run it three times before quoting a number - one run is an
    anecdote.
    """
    raise NotImplementedError("Sunday PM: live eval loop.")


def run_replay(questions: list[dict], *, fixture_dir: Path = FIXTURES) -> Summary:
    """Re-score recorded responses. No network, no credentials, no cost.

    TODO Sun PM: load each fixture and run the *same* scoring path as run_live.
    If the two modes can score differently, replay is theatre.
    """
    raise NotImplementedError("Sunday PM: replay scoring.")


def compare_to_baseline(current: Summary, baseline: dict) -> tuple[bool, list[str]]:
    """Return (passed, findings). Only regressions beyond tolerance fail;
    improvements and new metrics are reported but never block."""
    findings: list[str] = []
    passed = True

    for name, tolerance in TOLERANCE.items():
        if name not in current.metrics:
            continue
        if name not in baseline.get("metrics", {}):
            findings.append(f"  NEW   {name}: {current.metrics[name]:.3f} (no baseline)")
            continue

        before = baseline["metrics"][name]
        after = current.metrics[name]
        delta = after - before

        if delta < -tolerance:
            passed = False
            findings.append(
                f"  FAIL  {name}: {before:.3f} -> {after:.3f} "
                f"({delta:+.3f}, tolerance {tolerance:.3f})"
            )
        elif delta > tolerance:
            findings.append(f"  UP    {name}: {before:.3f} -> {after:.3f} ({delta:+.3f})")
        else:
            findings.append(f"  ok    {name}: {before:.3f} -> {after:.3f} ({delta:+.3f})")

    return passed, findings


def write_report(summary: Summary) -> Path:
    """Write the markdown report uploaded as a CI artifact."""
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{summary.run_id}.md"

    lines = [
        f"# Eval run {summary.run_id}",
        "",
        f"- mode: `{summary.mode}`",
        f"- semantic re-ranker: **{'on' if summary.use_reranker else 'off'}**",
        f"- questions: {summary.n_questions}",
        "",
        "## Metrics",
        "",
        "| metric | value |",
        "| --- | --- |",
    ]
    lines += [f"| {k} | {v:.3f} |" for k, v in sorted(summary.metrics.items())]

    if summary.cost:
        lines += ["", "## Cost", "", "| item | value |", "| --- | --- |"]
        lines += [f"| {k} | {v} |" for k, v in sorted(summary.cost.items())]

    failures = [q for q in summary.per_question if not q.get("passed", True)]
    if failures:
        lines += ["", f"## Failures ({len(failures)})", ""]
        lines += [f"- `{q['id']}` - {q.get('why', 'see JSON')}" for q in failures]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def summarise_runs(summaries: list[Summary], metric: str) -> str:
    """Mean and spread across repeated runs.

    If the spread is wider than the difference you want to claim, there is no
    result yet - only noise. Say that rather than rounding in your own favour.
    """
    values = [s.metrics[metric] for s in summaries if metric in s.metrics]
    if len(values) < 2:
        return f"{metric}: {values[0]:.3f} (single run - not yet quotable)" if values else ""
    return (
        f"{metric}: mean {statistics.mean(values):.3f}, "
        f"range {min(values):.3f}-{max(values):.3f}, n={len(values)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true", help="Call the deployed API.")
    mode.add_argument("--replay", action="store_true", help="Score recorded fixtures.")

    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument(
        "--no-reranker",
        action="store_true",
        help="The comparison arm for the headline experiment.",
    )
    parser.add_argument("--gate", type=Path, help="Baseline JSON to compare against.")
    parser.add_argument("--out", type=Path, help="Write the summary JSON here.")
    args = parser.parse_args()

    questions = load_questions()
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if args.live:
        summary = run_live(questions, api_url=args.api_url, use_reranker=not args.no_reranker)
    else:
        summary = run_replay(questions)

    summary.run_id = run_id
    report = write_report(summary)
    print(f"report: {report}")

    if args.out:
        args.out.write_text(json.dumps(summary.to_json(), indent=2), encoding="utf-8")

    if args.gate:
        baseline = json.loads(args.gate.read_text(encoding="utf-8"))
        passed, findings = compare_to_baseline(summary, baseline)
        print(f"\ngate vs {args.gate.name}:")
        print("\n".join(findings))
        if not passed:
            print("\nRegression beyond tolerance.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
