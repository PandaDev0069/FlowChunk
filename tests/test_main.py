import runpy
from pathlib import Path
from unittest.mock import patch

from main import main


@patch("main.uvicorn.run")
def test_main_calls_uvicorn_run(mock_run):
    main()

    mock_run.assert_called_once_with(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


@patch("uvicorn.run")
def test_main_entry_point(mock_run):
    project_root = Path(__file__).resolve().parent.parent
    runpy.run_path(str(project_root / "main.py"), run_name="__main__")
    mock_run.assert_called_once_with(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
