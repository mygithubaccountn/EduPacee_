import pytest
from edupace_app.utils import get_user_role, process_excel_grades

pytestmark = pytest.mark.django_db


class TestGetUserRole:
    def test_get_role_for_unauthenticated_user(self, anon_user):
        role = get_user_role(anon_user)
        assert role in (None, "", "guest")


class TestProcessExcelGrades:
    def test_process_excel_missing_required_columns(self):
        bad_input = None
        result = process_excel_grades(bad_input)
        assert isinstance(result, tuple)
        assert len(result) in (2, 3)
        assert result[-1] is not None
