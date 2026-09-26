from pathlib import Path


BOOTSTRAP = Path(__file__).parents[1] / "scripts" / "bootstrap_github_oidc.sh"
GUARD_MARKER = "RETIRED_AZURE_BOOTSTRAP_GUARD"
GUARD_EXIT = "exit 78"


def test_retired_azure_bootstrap_fails_closed_before_legacy_logic():
    script = BOOTSTRAP.read_text(encoding="utf-8")
    lines = script.splitlines()

    marker_line = next(
        index for index, line in enumerate(lines) if GUARD_MARKER in line
    )
    exit_line = lines.index(GUARD_EXIT)
    legacy_logic_line = next(
        index
        for index, line in enumerate(lines)
        if line.startswith('EXPECTED_SUBSCRIPTION_ID=')
    )
    first_azure_cli_line = next(
        index for index, line in enumerate(lines) if "command -v az" in line
    )
    guard = "\n".join(lines[marker_line:legacy_logic_line])

    assert marker_line < exit_line < legacy_logic_line < first_azure_cli_line
    assert lines[exit_line] == GUARD_EXIT
    assert "superseded and intentionally disabled" in guard
    assert "README.md#security-model" in guard
    assert "no supported bypass" in guard
