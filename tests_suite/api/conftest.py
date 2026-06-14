import pytest

from django.test import Client
from django.contrib.auth.models import User


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="2026112345",
        email="aluno@ifrn.edu.br",
        password="senha123"
    )


@pytest.fixture
def authenticated_client(test_user):
    client = Client()
    client.force_login(test_user)
    return client


@pytest.fixture
def anonymous_client():
    return Client()