from unittest.mock import MagicMock, patch

from app.tasks.cleanup import run_user_cleanup


@patch("app.tasks.cleanup.UserRepository.permanently_delete_soft_deleted_users")
def test_run_user_cleanup_calls_repository(mock_delete):
    db = MagicMock()
    mock_delete.return_value = 3

    run_user_cleanup(db)

    mock_delete.assert_called_once_with(db)


@patch("app.tasks.cleanup.UserRepository.permanently_delete_soft_deleted_users")
@patch("builtins.print")
def test_run_user_cleanup_prints_deleted_count(
    mock_print,
    mock_delete,
):
    db = MagicMock()
    mock_delete.return_value = 5

    run_user_cleanup(db)

    mock_print.assert_called_once_with("Successfully cleaned up 5 soft-deleted users.")
