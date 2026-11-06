# Corpus attribution

The corpus is the **Australian Privacy Principles guidelines** published by the
Office of the Australian Information Commissioner.

Source: <https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines>

## Licence

OAIC website content is licensed under the
[Creative Commons Attribution 4.0 International Licence](https://creativecommons.org/licenses/by/4.0/)
(CC BY 4.0), per <https://www.oaic.gov.au/about-the-OAIC/copyright>. Verified
2026-11-06.

Excluded from that licence: third-party content, the OAIC logo, the
Commonwealth Coat of Arms, trademarked material, and images and photographs.
`scripts/fetch_corpus.py` takes the text of each guidance chapter only, so
none of the excluded material is reproduced here.

## Required attribution

OAIC specifies this wording:

> Office of the Australian Information Commissioner website – www.oaic.gov.au

© Commonwealth of Australia.

## Why the documents are not committed

`data/sample-corpus/` holds a manifest and this file, not the text. Fetch it
with `python scripts/fetch_corpus.py`.

Two reasons. Redistributing someone else's content from a portfolio repo is
avoidable, and the fetch is reproducible in a minute. More usefully, it keeps
the corpus a *version* rather than a snapshot: the guidelines get amended, and a
committed copy would silently drift away from the source the citations point at.

## Not legal advice

This is a retrieval and evaluation exercise. The assistant answers from the
guidance text and cites it; it is not a compliance tool and its output is not
legal advice. The README says the same thing where a reader will see it.
