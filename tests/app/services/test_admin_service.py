from unittest.mock import patch
from uuid import uuid4

from app.services.admin_service import AdminService


class TestAdminService:
    @patch(
        "app.repositories.user_repository.UserRepository.permanently_delete_soft_deleted_users"
    )
    def test_permanently_delete_soft_deleted_users(
        self,
        mock_delete,
        db_session,
    ):
        mock_delete.return_value = 5

        result = AdminService.permanently_delete_soft_deleted_users(db_session)

        mock_delete.assert_called_once_with(db_session)
        assert result == 5

    @patch("app.repositories.user_repository.UserRepository.hard_delete_user")
    def test_hard_delete_user_success(
        self,
        mock_hard_delete,
        db_session,
    ):
        user_id = uuid4()
        mock_hard_delete.return_value = True

        result = AdminService.hard_delete_user(
            user_id,
            db_session,
        )

        mock_hard_delete.assert_called_once_with(
            db_session,
            user_id,
        )
        assert result is True

    @patch("app.repositories.user_repository.UserRepository.hard_delete_user")
    def test_hard_delete_user_failure(
        self,
        mock_hard_delete,
        db_session,
    ):
        user_id = uuid4()
        mock_hard_delete.return_value = False

        result = AdminService.hard_delete_user(
            user_id,
            db_session,
        )

        mock_hard_delete.assert_called_once_with(
            db_session,
            user_id,
        )
        assert result is False
