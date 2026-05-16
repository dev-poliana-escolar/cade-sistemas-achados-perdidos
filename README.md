[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/JZ9UDrFW)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23269651&assignment_repo_type=AssignmentRepo)

# SUMÁRIO
1. [Sobre o sistema](#cade-sistemas-de-achados-e-perdidos)
2. [Como executar o sistema](#como-executar-o-projeto)

# CADE: Sistemas de achados e perdidos

O sistema de achados e perdidos do Instituto Federal do Rio Grande do Norte (IFRN), campus Parnamirim, tem como objetivo permitir que alunos e servidores consultem e cadastrem itens perdidos de forma remota, além de automatizar os processos de doação e o ciclo de vida dos objetos encontrados.

#### Ferramentas de IA utilizadas:
Qwen, NotebookLLM e Claude

#### Documento de decisão de arquitetura:
[Architecture Decision Record](docs/ADR-001.md)

#### Scaffolding
```
projeto-final-grupo2-poliana-kaua-matheus
    ├── backend
    │   ├── apps
    │   │   ├── audit
    │   │   ├── claims
    │   │   ├── donations
    │   │   ├── items
    |   ├── Dockerfile    
    │   ├── core
    │   ├── media
    |   ├── requirements.txt
    │   ├── static
    │   └── templates
    ├── docker-compose.yml
    ├── docs
    ├──  frontend
    |    └── src
    ├── LICENSE
    └── README.md

```

# Como executar o sistema

1. Crie um ambiente virtual
    ```bash
    python -m venv .venv
    ```
    **Ative o ambiente virtual**\
    1.1 Se estiver no Windows
    ```bash
    source .venv/Scripts/activate
    ``` 
    1.2 Se estiver no Linux
    ```bash
    source .venv/bin/activate
    ```

2. Instale as depedências
    ```bash
    cd backend # entre na pasta designada ao backend
    pip install -r requirements.txt
    ```
3. Crie o arquivo `.env`
    ```bash
    touch .env
    ```
    
    -  Copie o arquivo `.env.example` e o **configure** o seu `.env`!

    3.1 Crie a secret key para o Django
    ```bash
    python -c 'import secrets; print(secrets.token_hex(32))' # cole a chave gerada
    ```
    - Defina a senha do banco de dados como: `cade234`

    **3.2 Consumo do SUAP/API**\
    1. Repositório que serviu de base: https://github.com/sergiodantasz/cliente-suap-django
    2. Repositorio oficial: https://github.com/ifrn-oficial/cliente_suap_django
    3. Documentação da API: https://suap.ifrn.edu.br/api/docs/


4. Suba o docker compose
    ```bash
    sudo docker compose up -d
    sudo docker ps -a # Exibição de todos os containers
    ```
    > Deve conter a imagem da aplicação e do postgrees

    | CONTAINER ID  | IMAGE   |         COMMAND                  |CREATED      |  STATUS     |               PORTS  |   NAMES |
    | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
    | #             | projeto-final-grupo2-poliana-kaua-matheus-web  | "python manage.py ru…" |  10 days ago  |  Exited (0) 10 days ago      |   |     cade_web |
    | # |  postgres:16  | "docker-entrypoint.s…"  |  10 days ago  |  Exited (0) 9 days ago |     |         cade_db|

    4.1 Caso já possua:
    ```bash
    sudo docker start cade_db # Foque apenas neste por enquanto
    sudo docker start cade_web 
    ```
    4.2 Dentro da pasta `/backend`, execute:
    ```bash
    python manage.py runserver
    ```
