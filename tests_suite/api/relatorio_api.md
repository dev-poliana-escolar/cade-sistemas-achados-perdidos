---
marp: true
theme: default
---

# Relatório de Implementação dos Testes de API

### SUMÁRIO
1. [Objetivo](#objetivo)\
a. [Estrutura de arquivos de testes](#estrutura-de-arquivos-de-testes)\
b. [Integração CI](#integração-ci)
2. [Tecnologias utilizadas](#tecnologias-utilizadas)
3. [Contrato da API](#contrato-da-api)
5. [Endpoints Testados](#endpoints-testados)
6. [Resultados Obtidos](#resultados-obtidos)\
a. [Atualizações](#atualizações)
7. [Inteligência Artificial](#uso-de-inteligência-artificial)

---

## Objetivo
Implementar uma suíte de testes automatizados para validação de endpoints da aplicação CADÊ, utilizando pytest, Django Test Client e validação de contratos com Pydantic, além da integração contínua por meio do GitHub Actions.

#### Estrutura de arquivos de testes:
```
tests_suite/
├── api
│   ├── conftest.py
│   ├── relatorio_api.md
│   ├── schemas
│   │   └── item_schemas.py
│   └── test_items.py
├── e2e
└── performance
```
---
#### Integração CI
```
.github/
└── workflows
    └── tests.yml
```

## Tecnologias Utilizadas

- pytest
- pydantic 
- Django Test Client
- GitHub Actions
---
## Contrato da API

Foi definido um [schema](./schemas/item_schemas.py) utilizando Pydantic para validar a estrutura dos dados retornados pelos endpoints da API.

--- 
Campos validados:

- id
- categoria
- descricao
- cor
- local_encontrado
- status
- dados_sensiveis
- cadastrado_por_id
- data_encontro

A validação garante conformidade entre a resposta da API e o contrato esperado pela aplicação.

---

## Endpoints Testados

**1. Consulta de Item**

Endpoint responsável por retornar os dados de um item específico.

Casos implementados:

- Sucesso: consulta de item existente por usuário autenticado.
- Erro: item inexistente (404).
- Erro: usuário não autenticado (302).

---
**2. Cadastro de Item**

Endpoint responsável pelo registro de novos itens.

Casos implementados:

- Sucesso: cadastro com dados válidos.
- Erro: envio de dados inválidos (400).
- Erro: usuário não autenticado (302).
---
**3. Cancelamento de Item**

    Endpoint responsável pelo cancelamento de itens pendentes.

    Casos implementados:

    - Sucesso: cancelamento de item pendente.
    - Erro: tentativa de cancelar item em estado não permitido (400).
    - Erro: usuário não autenticado (302).
---
## Resultados Obtidos

Execução da suíte de testes:

``` bash
====================================================================================================== test session starts ======================================================================================================
platform linux -- Python 3.12.1, pytest-9.0.2, pluggy-1.6.0
django: version: 6.0.4, settings: core.settings (from ini)
rootdir: /workspaces/projeto-final-grupo2-poliana-kaua-matheus
configfile: pytest.ini
plugins: django-4.12.0, base-url-2.1.0, html-4.2.0, playwright-0.8.0, anyio-4.13.0, metadata-3.1.1
collected 9 items                                                                                                                                                                                                               

tests_suite/api/test_items.py .........                                                                                                                                                                                   [100%]

======================================================================================================= 9 passed in 4.65s =======================================================================================================
```

Todos os cenários previstos foram executados com sucesso.

---

### Atualizações
Esta seção documenta mudanças de comportamentos da API.

1. [api_views.py](../../apps/items/api_views.py) : `@login_required` -> `@api_login_required`  
    A mudança de `@login_required` (nativo do Django) para o `@api_login_required` (customizado) foi feita para garantir que a API responda no formato correto (JSON) quando um usuário não estiver autenticado.


---
# Integração Contínua

Foi configurado um workflow no GitHub Actions para execução automática da suíte de testes em eventos de push e pull request.

**O pipeline realiza:**

1. Configuração do ambiente Python.
2. Instalação das dependências do projeto.
3. Inicialização do PostgreSQL/Docker.
4. Execução das migrações do Django.
5. Execução dos testes automatizados com pytest.

---
**Resultado:**

- Pipeline executado com sucesso.
- Todos os testes aprovados.
- Ambiente de CI validado.


---
## Uso de Inteligência Artificial

Chat GPT, ferramenta de IA utilizada como apoio na geração inicial dos casos de teste, definição dos cenários de sucesso e erro e construção do contrato de validação da API utilizando Pydantic.
