import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".claude" / "skills" / "article-forge" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "tools"))

import check_specs  # noqa: E402
import scenario_audit  # noqa: E402

ENGINE_REPO = scenario_audit.is_engine_repo(ROOT)


def pytest_bdd_apply_tag(tag, function):
    """@eval:<case> scenarios test Claude's behaviour, so `claude plugin eval` runs them.
    Here they are reported as skipped, which keeps them visible in every test run.

    @upstream scenarios check the public engine repo itself, so a writer's copy skips them.
    @id:NNN-NN is a stable scenario ID for the ledger, not a pytest mark.
    """
    if tag.startswith("id:"):
        return True
    if tag == "upstream":
        if not ENGINE_REPO:
            pytest.mark.skip(reason="checks the public engine repo only")(function)
        return True
    if tag.startswith("eval:"):
        case = tag.split(":", 1)[1]
        pytest.mark.skip(reason=f"behaviour scenario: claude plugin eval --case {case}")(function)
        return True
    return None


def _scenario_key(item):
    try:
        from pytest_bdd.scenario import scenario_wrapper_template_registry
    except ImportError:  # pragma: no cover
        return None
    scenario = scenario_wrapper_template_registry.get(getattr(item, "obj", None))
    if scenario is None:
        return None
    return Path(scenario.feature.filename).name, scenario.name


def pytest_collection_modifyitems(session, config, items):
    keys = {}
    for item in items:
        key = _scenario_key(item)
        if key:
            keys[item.nodeid] = key
    config._af_keys = keys
    test_files = {p.resolve() for d in (ROOT / "tests", ROOT / "local" / "tests") if d.is_dir()
                  for p in d.glob("test_*.py")}
    collected_files = {Path(str(item.fspath)).resolve() for item in items}
    config._af_full_run = test_files <= collected_files and not config.getoption("keyword") \
        and not config.getoption("markexpr")
    config._af_skipped = {}


def pytest_runtest_logreport(report):
    config = getattr(pytest_runtest_logreport, "_config", None)
    if config is None or not report.skipped:
        return
    key = getattr(config, "_af_keys", {}).get(report.nodeid)
    if key:
        reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
        config._af_skipped[key] = reason.removeprefix("Skipped: ")


def pytest_configure(config):
    pytest_runtest_logreport._config = config


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    if not hasattr(config, "_af_keys") or exitstatus not in (0, 1):
        return
    expected = scenario_audit.expected_scenarios(check_specs.check(ROOT).ids)
    problems = scenario_audit.audit(expected, set(config._af_keys.values()), config._af_skipped,
                                    config._af_full_run, ENGINE_REPO)
    if problems:
        tr = config.pluginmanager.get_plugin("terminalreporter")
        for p in problems:
            (tr.write_line if tr else print)(f"SCENARIO AUDIT: {p}")
        session.exitstatus = 1
