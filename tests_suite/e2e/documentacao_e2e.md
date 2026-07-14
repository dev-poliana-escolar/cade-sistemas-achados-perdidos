
# Guia de Execução dos Testes E2E — Playwright + Pytest

# Objetivo

Este documento descreve o processo de instalação, configuração e execução dos testes automatizados de interface (E2E) desenvolvidos com **Playwright** e **Pytest** para o sistema **CADE**.

Os testes automatizam os principais fluxos da aplicação, incluindo autenticação e navegação entre funcionalidades críticas do sistema.

---

# Pré-requisitos

Antes de executar os testes, certifique-se de possuir:

* Python 3.10 ou superior
* Ambiente virtual configurado
* Docker instalado
* Banco de dados do projeto ativo
* Projeto CADE em execução localmente

---

# Inicialização da Aplicação

Os testes dependem da aplicação estar disponível durante a execução.

## Iniciar o Banco de Dados

Verifique se o container do banco de dados está ativo:

```bash
docker ps
```

# Configuração Inicial do Ambiente

Execute esta etapa apenas na primeira configuração da máquina.

## Ativar o Ambiente Virtual

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

---

## Iniciar o Servidor Django

Em um terminal, execute:

```bash
python manage.py runserver
```

A aplicação deverá estar acessível em:

```text
http://127.0.0.1:8000
```
---



---

## Instalar Dependências

```bash
pip install -r requirements.txt
```

---

### Organização adotada

* **Pages**: implementação do padrão Page Object Model (POM).
* **Tests**: cenários automatizados.
* **Conftest**: fixtures compartilhadas.

---

Essa abordagem reduz a fragilidade dos testes frente a alterações visuais da aplicação.

---

# Execução dos Testes

Com o ambiente virtual ativo e a aplicação em execução, execute:

```bash
pytest tests_suite/e2e/ --browser firefox --html=relatorio_e2e.html --self-contained-html --screenshot=only-on-failure --video=retain-on-failure --headed
```

---

# Evidências Geradas

Ao término da execução, serão produzidas evidências automáticas:

## Relatório HTML

```text
relatorio_e2e.html
```

---

# Fluxos Automatizados

## Teste feito:

Valida:

* Acesso à página de autenticação;
* Preenchimento de credenciais;
* Submissão do cadastro do item;
* Redirecionamento após login.

---

# Gravação Inicial com Codegen

Os fluxos foram inicialmente capturados utilizando o Playwright Codegen.

Comando utilizado:

```bash
playwright codegen http://localhost:8000
```

Após a gravação, os scripts gerados foram refinados manualmente utilizando:

Copie o código e jogue na pasta:
```text
/tests_suite/e2e/nome_do_test_novo.py
```

---

# Resultado Esperado

Ao final da execução, espera-se:

* O teste aprovado;
* Relatório HTML gerado;
* Evidências disponíveis para auditoria;
* Execução reproduzível em ambiente local.

---

Após a execução:

```bash
xdg-open relatorio_e2e.html
```
ou abra o arquivo manualmente no navegador.