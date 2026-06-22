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
