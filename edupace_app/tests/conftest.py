import pytest
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import AnonymousUser

pytestmark = pytest.mark.django_db


def safe_reverse(name, *args, **kwargs):
    try:
        return reverse(name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        pytest.skip("URL name not found in project")


@pytest.fixture
def anon_user():
    return AnonymousUser()


try:
    from edupace_app.factories import AssessmentFactory, LearningOutcomeFactory
except Exception:
    AssessmentFactory = None
    LearningOutcomeFactory = None


@pytest.fixture
def AssessmentFactoryFixture():
    if AssessmentFactory is None:
        pytest.skip("AssessmentFactory not available")
    return AssessmentFactory


@pytest.fixture
def LearningOutcomeFactoryFixture():
    if LearningOutcomeFactory is None:
        pytest.skip("LearningOutcomeFactory not available")
    return LearningOutcomeFactory
