[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/JZ9UDrFW)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23269651&assignment_repo_type=AssignmentRepo)

# SUMÁRIO
1. [Sobre o sistema](#cade-sistemas-de-achados-e-perdidos)
2. [Como executar o sistema](#como-executar-o-sistema)

# CADE: Sistemas de achados e perdidos

O sistema de achados e perdidos do Instituto Federal do Rio Grande do Norte (IFRN), campus Parnamirim, tem como objetivo permitir que alunos e servidores consultem itens encontrados e realizem  reportes de itens perdidos de forma remota, além de automatizar os processos de doação e o ciclo de vida dos objetos encontrados.

#### Ferramentas de IA utilizadas:
1. Para apoio: Qwen, NotebookLLM, Claude, ChatGPT
2. Para consumo de API: Gemini (https://aistudio.google.com/)

#### Documento de decisão de arquitetura:
[Architecture Decision Record](docs/ADR-001.md)

#### Scaffolding

```text
projeto-final-grupo2-poliana-kaua-matheus
├── apps
│   ├── analysis
│   ├── category
│   ├── color
│   ├── donations
│   ├── items
│   └── report
├── core
├── docs
│   └── images
│       └── diagrams
├── media
│   └── items
├── static
├── templates
│   ├── admin
│   ├── analysis
│   ├── items
│   ├── partials
│   │   ├── analysis
│   │   ├── items
│   │   └── report
│   └── report
├── tests_suite
│   ├── api
│   │   └── schemas
│   ├── e2e
│   └── performance
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── LICENSE
└── README.md
```
# Como executar o sistema?

O projeto pode ser executado de duas formas:

- **Com Docker (recomendado)**: não é necessário instalar Python nem PostgreSQL localmente.
- **Localmente**: utilizando um ambiente virtual Python e um banco PostgreSQL executando em Docker.

---

## Opção 1 - Executando com Docker (recomendado)

### 1. Crie o arquivo `.env`

```bash
cp .env.example .env
```

Configure as variáveis de ambiente.

> Para execução via Docker, altere:
```text
 DB_HOST=db
```

Configure também:

- `SECRET_KEY`
    ```bash
    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    ```
- `GEMINI_API_KEY`
- Credenciais do SUAP:  
    1. Repositório que serviu de base: https://github.com/sergiodantasz/cliente-suap-django     
    2. Repositorio oficial: https://github.com/ifrn-oficial/cliente_suap_django     
    3. Documentação da API: https://suap.ifrn.edu.br/api/docs/

---

### 2. Execute o projeto

```bash
sudo docker compose up --build
```

Na primeira execução a imagem será construída automaticamente.

Depois disso, basta executar:

```bash
sudo docker compose up
```

A aplicação ficará disponível em:

```
http://localhost:8000
```

Para finalizar:

```bash
sudo docker compose down
```

### 3. Para criar super usuário
> Enquanto os containers rodam, você pode em outro terminal:
```bash
sudo docker compose exec web python manage.py createsuperuser
```

---

## Opção 2 - Executando localmente

### 1. Crie o ambiente virtual

```bash
python -m venv .venv
```

#### Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

---

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

---

### 3. Configure o `.env`

```bash
cp .env.example .env
```

Para execução local utilize:

```text
DB_HOST=localhost
```

Configure também:

- `SECRET_KEY`
    ```bash
    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    ```
- `GEMINI_API_KEY`
- Credenciais do SUAP:  
    1. Repositório que serviu de base: https://github.com/sergiodantasz/cliente-suap-django     
    2. Repositorio oficial: https://github.com/ifrn-oficial/cliente_suap_django     
    3. Documentação da API: https://suap.ifrn.edu.br/api/docs/


---

### 4. Inicie o PostgreSQL

```bash
sudo docker compose up -d db
```

ou

```bash
sudo docker start cade_db
```

---

### 5. Execute a aplicação

```bash
python manage.py migrate
python manage.py runserver
```
---

# Testes e Qualidade de Software

O projeto conta com uma suíte de testes automatizados cobrindo diferentes cenários e objetivos.
> wip(13/07/2026) : No momento estão desatualizados 
- [Guia de Execução dos Testes E2E (Playwright + Pytest)](./tests_suite/e2e/documentacao_e2e.md)
- [Relatório e Guia de Testes de Performance (k6)](./tests_suite/performance/relatorio_testes.md)
