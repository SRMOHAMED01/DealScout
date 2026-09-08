"""
Regression tests for P0 syntax and import issues.
"""

import compileall
from pathlib import Path


def test_no_syntax_errors_in_project():
    """Ensure all python files in dealscout compile without SyntaxError."""
    project_root = Path(__file__).resolve().parent.parent
    result = compileall.compile_dir(str(project_root), quiet=1)
    assert result is True, "One or more Python files failed compilation"


def test_import_company_modules():
    """Verify company_generator and company_db_connector import cleanly."""
    from ingestion.generators import company_generator
    from ingestion.connectors import company_db_connector

    assert hasattr(company_generator, "generate_companies")
    assert hasattr(company_db_connector, "fetch_company_by_id")
    assert hasattr(company_db_connector, "fetch_company_metadata")
