"""specs/002 is behaviour-only: every scenario is @eval and reported as skipped here.

Binding the file still proves it parses as valid Gherkin.
"""

from pytest_bdd import scenarios

scenarios("../specs/002-provenance-subcuts.feature")
