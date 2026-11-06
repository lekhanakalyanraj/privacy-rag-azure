"""The four metrics, split by what they need:

  retrieval.py    arithmetic - no model, deterministic
  citations.py    half mechanical, half judged
  groundedness.py judged
  abstention.py   comparison - no model

recall@5 is defensible without caveats; groundedness always comes with
"according to a judge that agreed with me G% of the time".
"""
