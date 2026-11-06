from rag_api.answer import (
    ABSTAIN_SENTINEL,
    build_messages,
    invalid_citations,
    is_abstention,
    parse_citations,
)


def test_parse_citations_in_order_of_first_use() -> None:
    text = "Consent is required [2]. Exceptions are narrow [1][2]."
    assert parse_citations(text) == [2, 1]


def test_parse_citations_handles_no_citations() -> None:
    assert parse_citations("A confident, unsourced claim.") == []


def test_invalid_citations_flags_out_of_range() -> None:
    """A model citing passage 7 when it was given 5 is hallucinating structure,
    and it is cheap to catch without a judge."""
    assert invalid_citations("Claim [7].", n_passages=5) == [7]
    assert invalid_citations("Claim [3].", n_passages=5) == []


def test_abstention_requires_the_exact_sentinel() -> None:
    assert is_abstention(ABSTAIN_SENTINEL)
    assert is_abstention(f"  {ABSTAIN_SENTINEL}\n")
    # Prose that merely sounds like a refusal must not count, or the metric
    # starts measuring the model's vocabulary instead of its behaviour.
    assert not is_abstention("I'm not sure this is covered by the documents.")


def test_build_messages_includes_passages_and_question() -> None:
    messages = build_messages("Do I need consent?", "[1] Some passage text")

    assert messages[0]["role"] == "system"
    assert ABSTAIN_SENTINEL in messages[0]["content"]
    assert "Do I need consent?" in messages[1]["content"]
    assert "[1] Some passage text" in messages[1]["content"]
