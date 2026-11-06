"""Shared fixtures.

Nothing here touches Azure. The modules worth unit-testing - chunking and
citation parsing - are deliberately pure functions, so the test suite runs in
CI on every pull request without credentials, without network, and in under a
second. Anything that needs the cloud belongs in eval/, not here.
"""

import pytest

SAMPLE_DOC = """# Privacy Principles Overview

This document summarises the handling of personal information.

## APP 7 Direct marketing

An organisation must not use personal information for direct marketing unless
an exception applies.

The exceptions are narrow and depend on how the information was collected.

## APP 8 Cross-border disclosure

Before disclosing personal information overseas, reasonable steps must be
taken to ensure the recipient does not breach the principles.
"""


@pytest.fixture
def sample_markdown() -> str:
    return SAMPLE_DOC
