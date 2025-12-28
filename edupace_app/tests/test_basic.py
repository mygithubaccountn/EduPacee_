"""
Basic smoke tests to verify test setup is working
"""
import pytest
from django.contrib.auth.models import User


def test_django_setup(db):
    """Test that Django is properly configured"""
    assert User.objects.count() == 0


def test_database_works(db):
    """Test that database operations work"""
    user = User.objects.create_user(
        username='test',
        password='test123'
    )
    assert User.objects.count() == 1
    assert User.objects.get(username='test') == user

