from unittest.mock import MagicMock, patch

from app.core.database import get_db


def test_get_db_yields_session_and_closes():
    mock_db = MagicMock()
    with patch("app.core.database.SessionLocal", return_value=mock_db):
        gen = get_db()
        session = next(gen)

        assert session is mock_db

        try:
            next(gen)
        except StopIteration:
            pass

        mock_db.close.assert_called_once()
