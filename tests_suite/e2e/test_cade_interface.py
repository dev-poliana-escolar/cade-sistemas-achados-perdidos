import os
import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth.models import User
from django.test import Client

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.fixture
def mock_session_cookie(db):
    """
    Cria o usuário e gera uma sessão válida. 
    Isso é feito fora do escopo principal do Playwright para evitar conflitos de threads.
    """
    user, _ = User.objects.get_or_create(
        username="20251148060019",
        defaults={"email": "aluno@ifrn.edu.br"}
    )
    user.set_password("password123")
    user.save()

    client = Client()
    client.force_login(user)
    
    return client.session.session_key

@pytest.mark.django_db(transaction=True)
def test_fluxo_sistema_cade_cadastro(page: Page, live_server, settings, mock_session_cookie):
    """
    Teste End-to-End validando a criação de um item pelo formulário principal.
    """
    
    context = page.context
    context.add_cookies([{
        "name": settings.SESSION_COOKIE_NAME,
        "value": mock_session_cookie,
        "domain": "localhost",
        "path": "/"
    }])

    page.goto(live_server.url)
    
    page.goto(f"{live_server.url}/items/")
    page.wait_for_url("**/items/**", timeout=10000)

    page.get_by_text("Cadastrar Item").click()
    
    page.get_by_label("Categoria:").select_option("MATERIAL_ESCOLAR")
    page.get_by_role("textbox", name="Descrição:").fill("esses")
    page.get_by_label("Cor predominante:").select_option("VERMELHO")
    page.get_by_role("textbox", name="Local onde foi encontrado:").fill("logo ali")
    page.get_by_role("textbox", name="Data encontro:").fill("2026-06-15")
    
    page.get_by_role("button", name="Salvar").click()

    expect(page.get_by_text("esses").first).to_be_visible()