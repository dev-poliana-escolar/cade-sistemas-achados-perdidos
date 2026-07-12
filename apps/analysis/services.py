# apps/analysis/services.py
from difflib import SequenceMatcher

from apps.items.models import Item
from apps.report.models import Reporte
from apps.analysis.models import Analise, Parecer


def _similaridade_texto(texto_a: str, texto_b: str) -> float:
    """Retorna similaridade entre 0 e 1 usando comparação de sequências."""
    a = (texto_a or "").strip().lower()
    b = (texto_b or "").strip().lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def comparar_itens(reporte_perdido: Reporte, item_candidato: Item) -> dict:
    """
    Compara o reporte PERDIDO (item + local + data) com um item candidato
    do estoque, considerando também o reporte ENCONTRADO associado a ele.
    Retorna convergências, inconsistências e um score de 0 a 100.
    """
    item_perdido = reporte_perdido.item

    reporte_candidato = (
        item_candidato.reportes.filter(
            tipo=Reporte.Tipo.ENCONTRADO
        )
        .order_by("data")
        .first()
    )

    convergencias = []
    inconsistencias = []

    pontos = 0
    penalidade = 0

    # Categoria (peso 20)
    if item_perdido.categoria_id == item_candidato.categoria_id:
        convergencias.append("Mesma categoria")
        pontos += 20
    else:
        inconsistencias.append("Categoria diferente")
        penalidade += 40

    # Cor (peso 15)
    if item_perdido.cor_id == item_candidato.cor_id:
        convergencias.append("Mesma cor")
        pontos += 15
    else:
        inconsistencias.append(
            f"Cor divergente ({item_perdido.cor} × {item_candidato.cor})"
        )
        penalidade += 10

    # Descrição (peso 30)
    sim_desc = _similaridade_texto(
        item_perdido.descricao,
        item_candidato.descricao,
    )

    pontos += round(sim_desc * 30)

    if sim_desc >= 0.75:
        convergencias.append("Descrição muito semelhante")

    elif sim_desc >= 0.50:
        convergencias.append("Descrição parcialmente semelhante")

    else:
        inconsistencias.append("Descrição pouco semelhante")
        penalidade += 10

    # Local (peso 20)
    if reporte_candidato:

        local1 = reporte_perdido.local.strip().lower()
        local2 = reporte_candidato.local.strip().lower()

        if local1 == local2:
            convergencias.append("Mesmo local")
            pontos += 20

        else:
            sim_local = _similaridade_texto(local1, local2)

            if sim_local >= 0.8:
                convergencias.append("Local semelhante")
                pontos += 12

            else:
                inconsistencias.append("Local divergente")
                penalidade += 15

    else:
        inconsistencias.append(
            "Local do item encontrado indisponível"
        )

    # Data/hora (peso 15)
    if (reporte_candidato and reporte_candidato.data and reporte_perdido.data):
        diff = (
            reporte_candidato.data -
            reporte_perdido.data
        ).days

        if diff < 0:

            inconsistencias.append(
                "Item encontrado antes da perda."
            )

            penalidade += 100

        elif diff <= 3:

            convergencias.append(
                "Datas muito próximas"
            )

            pontos += 15

        elif diff <= 15:

            convergencias.append(
                "Datas relativamente próximas"
            )

            pontos += 8

        elif diff <= 60:

            inconsistencias.append(
                "Datas relativamente distantes"
            )

            penalidade += 10

        elif diff <= 365:

            inconsistencias.append(
                "Datas muito distantes"
            )

            penalidade += 25

        else:

            inconsistencias.append(
                "Datas incompatíveis"
            )

            penalidade += 60

    else:
        inconsistencias.append(
            "Não foi possível comparar as datas."
        )

    score = max(0, pontos - penalidade)
    score = min(score, 100)

    if score >= 85:
        recomendacao = (
            "Alta probabilidade de correspondência."
        )

    elif score >= 65:
        recomendacao = (
            "Correspondência provável. "
            "Recomenda-se conferência física."
        )

    elif score >= 40:
        recomendacao = (
            "Correspondência possível, porém inconclusiva."
        )

    else:
        recomendacao = (
            "Baixa probabilidade de correspondência."
        )

    return {
        "item_candidato_id": item_candidato.id,
        "score": score,
        "convergencias": convergencias,
        "inconsistencias": inconsistencias,
        "recomendacao": recomendacao
    }


def gerar_parecer(analise: Analise) -> Parecer:
    """
    Gera (ou atualiza) o Parecer de uma Análise, comparando o reporte
    perdido com todos os itens candidatos disponíveis no estoque.
    """
    reporte_perdido = analise.reporte
    item_perdido = reporte_perdido.item

    candidatos = Item.objects.filter(
        status=Item.Status.NO_ESTOQUE,
        categoria=item_perdido.categoria,
    )

    resultados = [
        comparar_itens(reporte_perdido, candidato) for candidato in candidatos
    ]

    resultados.sort(key=lambda r: r["score"], reverse=True)

    if resultados:
        score_final = resultados[0]["score"]

        if score_final >= 70:
            recomendacao = (
                f"Alta probabilidade de correspondência com o item "
                f"#{resultados[0]['item_candidato_id']}."
            )
        elif score_final >= 40:
            recomendacao = (
                "Correspondência possível. Recomenda-se análise manual."
            )
        else:
            recomendacao = "Nenhum candidato apresentou correspondência satisfatória."
    else:
        score_final = 0
        recomendacao = "Nenhum item disponível para comparação."

    parecer, _ = Parecer.objects.update_or_create(
        analise=analise,
        defaults={
            "score_confianca": score_final,
            "convergencias": resultados,
            "inconsistencias": [],
            "recomendacao": recomendacao,
        },
    )

    return parecer