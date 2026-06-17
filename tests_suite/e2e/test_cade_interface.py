import pytest
from playwright.sync_api import Page, expect

def test_fluxo_sistema_cade(page: Page, live_server):
    page.goto(live_server.url)  # URL dinâmica (ex: http://localhost:53821)
    
    page.get_by_role("link", name="Entrar com SUAP").click()
    
    page.get_by_role("textbox", name="Usuário:").fill("20251148060019")
    page.get_by_role("textbox", name="Senha:").fill("Mel2020gor.")
    
    page.get_by_role("button", name="Acessar").click()
    page.wait_for_url("**/items/**", timeout=10000)
    
    page.get_by_text("Cadastrar Item").click()
    
    page.get_by_label("Categoria:").select_option("MATERIAL_ESCOLAR")
    page.get_by_role("textbox", name="Descrição:").fill("esses")
    page.get_by_label("Cor predominante:").select_option("VERMELHO")
    page.get_by_role("textbox", name="Local onde foi encontrado:").fill("logo ali")
    page.get_by_role("textbox", name="Data encontro:").fill("2026-06-15")
    
    page.get_by_role("button", name="Salvar").click()

    expect(page.get_by_text("esses").first).to_be_visible()