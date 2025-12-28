import pytest

pytestmark = pytest.mark.django_db


class TestAssessmentGradeForm:
    def test_assessment_grade_form_querysets(self, AssessmentFactoryFixture):
        assessment = AssessmentFactoryFixture()
        assert assessment is not None

    def test_assessment_grade_form_valid_data(self, AssessmentFactoryFixture):
        assessment = AssessmentFactoryFixture()
        assert assessment is not None


class TestAssessmentToLOForm:
    def test_assessment_to_lo_form_querysets(self, AssessmentFactoryFixture):
        assessment = AssessmentFactoryFixture()
        assert assessment is not None


class TestLOToPOForm:
    def test_lo_to_po_form_querysets(self, LearningOutcomeFactoryFixture):
        lo = LearningOutcomeFactoryFixture()
        assert lo is not None
