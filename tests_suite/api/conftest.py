import pytest

from django.test import Client
from django.contrib.auth.models import User
from unittest.mock import Mock


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="2026112345",
        email="aluno@ifrn.edu.br",
        password="senha123"
    )


@pytest.fixture
def authenticated_client(user):
    client = Client()
    client.force_login(user)
    return client

@pytest.fixture
def mock_api_auth(monkeypatch, user):
    def mock_process_request(self, request):
        request.user = user
        return None
    return user