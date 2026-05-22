"""Architecture tests: verify the Clean Architecture dependency rule via import-linter."""

import shutil
import subprocess


def test_import_contracts_pass() -> None:
    """All domains must satisfy the Clean Architecture dependency rule.

    Verifies that domain and application layers do not import framework
    packages (fastapi, sqlalchemy, pydantic, alembic), enforcing the
    dependency rule from SRS §4.2.
    """
    lint_imports = shutil.which("lint-imports")
    assert lint_imports is not None, "lint-imports binary not found on PATH"

    result = subprocess.run(
        [lint_imports, "--config", "pyproject.toml"],
        capture_output=True,
        text=True,
        cwd=".",  # run from web/backend/
    )
    assert result.returncode == 0, f"Import contracts failed:\n{result.stdout}\n{result.stderr}"
