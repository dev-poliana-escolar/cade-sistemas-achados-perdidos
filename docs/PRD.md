# SUMÁRIO
1. [PRD — Product Requirements Document](#1-prd--product-requirements-document)\
    1.1 [Visão Geral](#11-visão-geral)\
    1.2 [Problemas Principais](#-problemas-principais)
2. [Público Alvo](#2-público-alvo)\
    2.1 [Perfis de usuário](#21-perfis-de-usuário)
3. [User Stories e Critérios de Aceite](#3-user-stories-e-critérios-de-aceite)
4. [Fluxo de IA](#4-fluxo-de-ia)\
    4.1 [Dicionário](#41-dicionário)

# 1. PRD — Product Requirements Document
### 📌 1.1 Visão Geral

O CADÊ é um sistema de achados e perdidos que permite aos usuários o registro de reportes de itens encontrados e perdidos. O sistema realiza o cruzamento inteligente de dados assistido por IA e gerencia a intermediação de doações automáticas em formato de sorteio ou doação direta para itens não reclamados. Diante disso, administradores controlam o fluxo de estoque, validam análises de correspondência e conduzem doações.

#### 🎯 Problemas Principais
| Problema | Impacto Atual | Como o CADÊ Resolve |
| :--- | :--- | :--- |
| Deslocamento desnecessário | Alunos e servidores precisam ir presencialmente à COAPAC apenas para verificar se seu item foi encontrado | Consulta remota de itens cadastrados no sistema através de reportes públicos de itens encontrados. |
| Processo de devolução ineficiente | Dificuldade em validar a posse do item e rastrear quem retirou o quê | Mapeamento de laudos de IA e telas de **Análise** estruturadas + registro centralizado em **Log de Auditoria** como comprovante digital. |
| Destinação inadequada de itens não reclamados | Itens esquecidos ocupam espaço físico sem critério claro de descarte ou doação | Monitoramento automático de prazo (30 dias) com alteração de status do item para doação e sistema de sorteio aleatório ou doação direta integrada. |
| Falta de transparência e rastreabilidade | Não há histórico claro de movimentações, gerando dúvidas e conflitos | **Log de Auditoria Global** imutável registrando todas as ações (inserções, atualizações e deleções), capturando o estado anterior e novo em JSONB. |

# 2. Público Alvo

### 2.1 Perfis de usuário

**a. Usuário Comum (Aluno/Servidor do IFRN)**
* **Necessidades:** Encontrar rapidamente um item perdido; cadastrar um reporte de item encontrado; acompanhar o status de suas análises; participar de sorteios de doação de forma justa.
* **Permissões no Sistema:** Autenticar-se via SUAP (OAuth2); cadastrar reportes (tipo 'encontrado' ou 'perdido'); visualizar itens disponíveis e itens destinados a doação; manifestar interesse em sorteios; visualizar logs de auditoria referentes às suas próprias ações.

**b. Administrador (Equipe da COAPAC)**
* **Necessidades:** Gerenciar o inventário físico do estoque; avaliar as correspondências geradas pela IA; controlar prazos de guarda (30 dias) e efetivar doações/sorteios.
* **Permissões no Sistema:** Todas as permissões do usuário comum; alterar o status logístico do item (`aguardando_entrega` para `no_estoque`); aprovar ou rejeitar registros de `Analise` inserindo a devida justificativa; disparar sorteios automáticos; consultar a tela completa de `Log_Auditoria`.

**c. SUAP (Sistema Externo de Autenticação)**
* **Papel:** Provedor de identidade institucional via OAuth2 fornecendo matrícula, nome e vínculo.

---

# 3. User Stories e Critérios de Aceite
Acesse a especificação: [User Stories e critérios de aceite](user_stories.md)

---

# 4. Fluxo de IA

O prompt abaixo serve para a geração de pareceres de correspondência. O sistema pré-analisa a relação entre um **Reporte de Perda** e um **Item Encontrado** candidato, gerando um registro estruturado para acelerar a decisão do administrador.

```json
{
  "system_prompt": "Você é um assistente especializado em validação de posse de itens perdidos. Compare a descrição do item físico encontrado com o reporte de perda do usuário e identifique: (1) pontos de convergência, (2) inconsistências ou contradições, (3) score de confiança (0-100%). Responda estritamente no esquema JSON para Function Calling.",
  
  "few_shot_examples": [
    {
      "item_cadastrado": "Chaveiro preto com pingente de bola de futebol, localizado no bloco B.",
      "reporte_perda": "Perdi meu chaveiro preto com uma bolinha de futebol azul perto do bloco B.",
      "resposta_esperada": {
        "convergencias": ["cor preta", "pingente de bola de futebol", "proximidade ao bloco B"],
        "inconsistencias": ["detalhe da cor da bola: item cadastrado não especifica a cor azul"],
        "score_confianca": 88,
        "recomendacao": "Alta probabilidade de posse legítima - sugerir validação física com o proprietário sobre os detalhes da bola."
      }
    }
  ],
  
  "function_calling": {
    "name": "registrar_parecer_ia",
    "parameters": {
      "score_confianca": "integer (0-100)",
      "convergencias": "array<string>",
      "inconsistencias": "array<string>",
      "recomendacao": "string",
      "prompt": "string"
    }
  }
}
```

### 4.1 Dicionário

1. `system_prompt`: É a instrução de identidade + a tarefa que a inteligência artificial deve fazer.
2. `few_shot_examples`: O JSON mostra para a IA **um exemplo de caso real** (um chaveiro encontrado vs. um chaveiro perdido) e **ensina como ela deve "pensar"** para chegar ao score de 88%
3. `function_calling`: Define uma estrutura chamada _`registrar_parecer_ia`_. Em vez de a IA responder um texto longo, ela vai preencher esses campos (como *score_confianca* e *recomendacao*) 