import os
import json
import logging
from django.conf import settings
from django.utils import timezone
from groq import Groq
from pydantic import BaseModel, ConfigDict
from apps.analysis.models import Analise, Parecer
from apps.items.models import Item
from apps.report.models import Reporte

logger = logging.getLogger(__name__)

MODEL_NAME = "openai/gpt-oss-20b"

client = Groq(
    api_key=getattr(settings, "GROQ_API_KEY", None)
    or os.environ.get("GROQ_API_KEY")
)

# Schema de saída. O Groq usa este schema para garantir a estrutura da resposta
class ComparacaoIA(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_candidato_id: int
    score: int
    convergencias: list[str]
    inconsistencias: list[str]

class ParecerIA(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparacoes: list[ComparacaoIA]
    recomendacao_geral: str

# Serialização dos dados em texto legível pro modelo
def _descrever_reporte_perdido(reporte: Reporte) -> str:
    item = reporte.item
    return (
        f"Categoria: {item.categoria}\n"
        f"Cor: {item.cor}\n"
        f"Descrição: {item.descricao}\n"
        f"Local da perda: {reporte.local}\n"
        f"Data da perda: {reporte.data.isoformat()}\n"
        f"Observações: {reporte.observacoes or '—'}"
    )

def _descrever_candidato(item: Item) -> str:
    reporte_encontrado = (
        item.reportes.filter(tipo=Reporte.Tipo.ENCONTRADO)
        .order_by("data")
        .first()
    )
    local = reporte_encontrado.local if reporte_encontrado else "—"
    data = reporte_encontrado.data.isoformat() if reporte_encontrado and reporte_encontrado.data else "—"

    return (
        f"ID: {item.id}\n"
        f"Categoria: {item.categoria}\n"
        f"Cor: {item.cor}\n"
        f"Descrição: {item.descricao}\n"
        f"Local onde foi encontrado: {local}\n"
        f"Data em que foi encontrado: {data}"
    )

# Few-shot: 4 cenários calibrando o modelo em ALTO, MÉDIO, BAIXO e NEGATIVO
# (não repetem o schema, ensinam o padrão de raciocínio e a calibração do score)
_EXEMPLO_ALTO = (
    "ITEM PERDIDO:\n"
    "Categoria: Eletrônico\nCor: Preto\nDescrição: Fone de ouvido bluetooth JBL, com estojo de carregamento arranhado\n"
    "Local da perda: Biblioteca Central\nData da perda: 2026-05-10T14:00:00\nObservações: —\n\n"
    "CANDIDATOS NO ESTOQUE:\n"
    "ID: 12\nCategoria: Eletrônico\nCor: Preto\nDescrição: Fone bluetooth sem fio, estojo com riscos\n"
    "Local onde foi encontrado: Biblioteca Central, 2º andar\nData em que foi encontrado: 2026-05-10T17:30:00",
    ParecerIA(
        comparacoes=[
            ComparacaoIA(
                item_candidato_id=12,
                score=90,
                convergencias=[
                    "Mesma categoria (Eletrônico)",
                    "Mesma cor (Preto)",
                    "Descrição compatível: ambos citam estojo arranhado/riscado",
                    "Mesmo local (Biblioteca Central)",
                    "Encontrado poucas horas após a perda, no mesmo dia",
                ],
                inconsistencias=[],
            ),
        ],
        recomendacao_geral=(
            "O item #12 apresenta forte correspondência com o item perdido: mesma "
            "categoria, cor, descrição fisicamente compatível, mesmo local e diferença "
            "de poucas horas entre a perda e o encontro. Recomenda-se conferência "
            "física para confirmação."
        ),
    ),
)

_EXEMPLO_MEDIO = (
    "ITEM PERDIDO:\n"
    "Categoria: Mochila\nCor: Azul\nDescrição: Mochila escolar com bolso frontal e alça esquerda rasgada\n"
    "Local da perda: Bloco B, sala 12\nData da perda: 2026-06-01T10:00:00\nObservações: —\n\n"
    "CANDIDATOS NO ESTOQUE:\n"
    "ID: 30\nCategoria: Mochila\nCor: Azul\nDescrição: Mochila com bolso frontal, sem detalhes sobre alças\n"
    "Local onde foi encontrado: Bloco C, corredor principal\nData em que foi encontrado: 2026-06-05T09:00:00",
    ParecerIA(
        comparacoes=[
            ComparacaoIA(
                item_candidato_id=30,
                score=55,
                convergencias=[
                    "Mesma categoria (Mochila)",
                    "Mesma cor (Azul)",
                    "Ambas descrições citam bolso frontal",
                ],
                inconsistencias=[
                    "Descrição do candidato não menciona a alça rasgada, detalhe distintivo do item perdido",
                    "Local diferente (Bloco B x Bloco C), embora próximos",
                    "Encontrado 4 dias após a perda — prazo plausível, mas não imediato",
                ],
            ),
        ],
        recomendacao_geral=(
            "O item #30 tem convergências relevantes (categoria, cor, bolso frontal), "
            "mas falta confirmação do detalhe mais distintivo do item perdido (alça "
            "rasgada) e o local diverge. Correspondência possível, porém inconclusiva — "
            "recomenda-se checar fisicamente o estado da alça antes de confirmar."
        ),
    ),
)

_EXEMPLO_BAIXO = (
    "ITEM PERDIDO:\n"
    "Categoria: Guarda-chuva\nCor: Preto\nDescrição: Guarda-chuva liso, cabo de madeira\n"
    "Local da perda: Refeitório\nData da perda: 2026-04-02T12:00:00\nObservações: —\n\n"
    "CANDIDATOS NO ESTOQUE:\n"
    "ID: 8\nCategoria: Guarda-chuva\nCor: Xadrez vermelho e branco\nDescrição: Guarda-chuva estampado, cabo plástico\n"
    "Local onde foi encontrado: Estacionamento\nData em que foi encontrado: 2026-04-20T08:00:00",
    ParecerIA(
        comparacoes=[
            ComparacaoIA(
                item_candidato_id=8,
                score=18,
                convergencias=["Mesma categoria (Guarda-chuva)"],
                inconsistencias=[
                    "Cor completamente diferente (Preto liso x Xadrez vermelho/branco)",
                    "Material do cabo diferente (madeira x plástico)",
                    "Local diferente (Refeitório x Estacionamento)",
                    "Encontrado 18 dias após a perda",
                ],
            ),
        ],
        recomendacao_geral=(
            "O item #8 só compartilha a categoria com o item perdido; cor, material, "
            "local e prazo divergem significativamente. Baixa probabilidade de "
            "correspondência."
        ),
    ),
)

_EXEMPLO_NEGATIVO = (
    "ITEM PERDIDO:\n"
    "Categoria: Eletrônico\nCor: Preto\nDescrição: a\n"
    "Local da perda: a\nData da perda: 4022-05-20T15:05:00\nObservações: —\n\n"
    "CANDIDATOS NO ESTOQUE:\n"
    "ID: 9\nCategoria: Eletrônico\nCor: Preto\nDescrição: a\n"
    "Local onde foi encontrado: a\nData em que foi encontrado: 5622-02-04T15:25:00",
    ParecerIA(
        comparacoes=[
            ComparacaoIA(
                item_candidato_id=9,
                score=3,
                convergencias=[
                    "Mesma categoria, cor, descrição e local informados (dados idênticos)"
                ],
                inconsistencias=[
                    "Diferença de aproximadamente 1600 anos entre a data da perda e a "
                    "data do encontro — logicamente impossível",
                    "A semelhança textual provavelmente é coincidência de dados de "
                    "teste/placeholder, não evidência real de correspondência",
                ],
            ),
        ],
        recomendacao_geral=(
            "Apesar da aparente identidade textual entre os registros, a diferença de "
            "datas é logicamente impossível (cerca de 1600 anos), o que invalida "
            "qualquer correspondência. O score foi forçado para próximo de zero. "
            "Recomenda-se verificar se há erro de cadastro de data em algum dos "
            "reportes antes de prosseguir."
        ),
    ),
)

_FEW_SHOT_TURNS = []
for entrada, saida in (_EXEMPLO_ALTO, _EXEMPLO_MEDIO, _EXEMPLO_BAIXO, _EXEMPLO_NEGATIVO):
    _FEW_SHOT_TURNS.append(("user", entrada))
    _FEW_SHOT_TURNS.append(("assistant", saida.model_dump_json()))


def _montar_messages(
    reporte_perdido: Reporte,
    candidatos: list[Item]
) -> tuple[list[dict], str]:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }
    ]

    for role, text in _FEW_SHOT_TURNS:
        messages.append({
            "role": role,
            "content": text,
        })

    candidatos_texto = "\n\n---\n\n".join(
        _descrever_candidato(c)
        for c in candidatos
    )

    entrada_real = (
        f"ITEM PERDIDO:\n"
        f"{_descrever_reporte_perdido(reporte_perdido)}\n\n"
        f"CANDIDATOS NO ESTOQUE:\n"
        f"{candidatos_texto}"
    )

    messages.append({
        "role": "user",
        "content": entrada_real,
    })

    return messages, entrada_real


# Função principal
SYSTEM_INSTRUCTION = (
    "Você atua como servidor responsável pelo setor de Achados e Perdidos do IFRN. "
    "Sua tarefa é analisar um item perdido e compará-lo com todos os itens encontrados "
    "disponíveis no estoque, atribuindo um score de 0 a 100 para cada candidato.\n\n"
    "FAIXAS DE SCORE (calibração obrigatória):\n"
    "- 80-100 (ALTO): categoria, cor e descrição fortemente compatíveis, local igual "
    "ou muito próximo, datas próximas (poucos dias).\n"
    "- 40-79 (MÉDIO): convergências relevantes mas com pelo menos uma lacuna ou "
    "divergência importante (detalhe distintivo ausente, local diferente porém "
    "plausível, ou prazo maior).\n"
    "- 1-39 (BAIXO): poucas convergências, principalmente só a categoria, com "
    "divergências claras em cor, descrição, local ou data.\n"
    "- 0-5 (INVÁLIDO/IMPOSSÍVEL): use OBRIGATORIAMENTE essa faixa, independente de "
    "quão parecidos os textos sejam, quando:\n"
    "  (a) o item foi 'encontrado' ANTES da data da perda.\n"
    "  (b) a diferença entre perda e encontro é de anos, décadas ou séculos sem "
    "justificativa plausível.\n"
    "  (c) nesses casos, a semelhança textual nunca deve compensar a impossibilidade "
    "temporal.\n"
    "Nesses casos, explique na inconsistência que a diferença temporal invalida a "
    "correspondência, mesmo que os demais campos sejam idênticos — semelhança textual "
    "nunca compensa uma impossibilidade lógica de data.\n\n"
    "Outras regras:\n"
    "- A categoria informada pode conter erro de cadastro pelo usuário. Utilize-a apenas como um dos critérios de comparação. "
    "Se descrição, cor, local e datas forem fortemente compatíveis, a divergência de categoria não deve impedir uma alta pontuação, mas deve ser registrada como inconsistência.\n"
    "- Pequenas diferenças de descrição não impedem uma boa correspondência.\n"
    "- Seja conservador e não invente informações que não estão nos dados fornecidos.\n"
    "- Responda apenas utilizando o schema informado."
)


def gerar_parecer_ia(analise: Analise) -> Parecer:
    """
    Gera (ou atualiza) o Parecer de uma Análise usando a Groq
    para comparar o reporte perdido com os itens candidatos no estoque.
    """

    reporte_perdido = analise.reporte

    candidatos = list(
        Item.objects.filter(
            status=Item.Status.NO_ESTOQUE,
        )
    )

    if not candidatos:
        parecer, _ = Parecer.objects.update_or_create(
            analise=analise,
            defaults={
                "score_correspondencia": 0,
                "convergencias": [],
                "inconsistencias": [],
                "recomendacao": "Nenhum item disponível para comparação.",
                "prompt": "",
                "data_prompt": timezone.now(),
            },
        )
        return parecer

    messages, entrada_real = _montar_messages(
        reporte_perdido,
        candidatos
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "parecer_ia",
                    "strict": True,
                    "schema": ParecerIA.model_json_schema(),
                },
            },
        )
   
    except Exception as e:
        logger.exception(
            "Falha ao gerar parecer usando Groq."
        )

        raise RuntimeError(
            "Não foi possível gerar o parecer com IA."
        ) from e

    try:
        conteudo = response.choices[0].message.content

        if not conteudo:
            raise RuntimeError(
                "A IA retornou uma resposta vazia."
            )

        resultado: ParecerIA = ParecerIA.model_validate(
            json.loads(conteudo)
        )

        comparacoes = sorted(
            [c.model_dump() for c in resultado.comparacoes],
            key=lambda r: r["score"],
            reverse=True,
        )

        score_final = (
            comparacoes[0]["score"]
            if comparacoes
            else 0
        )

        parecer, _ = Parecer.objects.update_or_create(
            analise=analise,
            defaults={
                "score_correspondencia": score_final,
                "convergencias": comparacoes,
                "inconsistencias": [
                    {
                        "item_candidato_id": c["item_candidato_id"],
                        "inconsistencias": c["inconsistencias"],
                    }
                    for c in comparacoes
                ],
                "recomendacao": resultado.recomendacao_geral,
                "prompt": entrada_real,
                "data_prompt": timezone.now(),
            },
        )

        return parecer

    except Exception as e:
        logger.exception(e)

        raise RuntimeError(
            "Erro ao processar a resposta da IA."
        ) from e