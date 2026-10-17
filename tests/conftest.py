import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "article-forge" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def pytest_bdd_apply_tag(tag, function):
    """@eval:<case> scenarios test Claude's behaviour, so `claude plugin eval` runs them.

    Here they are reported as skipped, which keeps them visible in every test run.
    """
    if tag.startswith("eval:"):
        case = tag.split(":", 1)[1]
        pytest.mark.skip(reason=f"behaviour scenario: claude plugin eval --case {case}")(function)
        return True
    return None
