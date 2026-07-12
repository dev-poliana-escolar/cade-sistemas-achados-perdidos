
from difflib import SequenceMatcher

from apps.items.models import Item
from apps.analysis.models import Analise, Parecer


def _similaridade_texto(texto_a: str, texto_b: str) -> float:
    """Retorna similaridade entre 0 e 1 usando comparação de sequências."""
    a = (texto_a or "").strip().lower()
    b = (texto_b or "").strip().lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def comparar_itens(item_perdido: Item, item_candidato: Item) -> dict:
    """
    Compara um item perdido com um item candidato do estoque.
    Retorna convergências, inconsistências e um score de 0 a 100.
    """
    convergencias = []
    inconsistencias = []
    pontos = 0
    pontos_max = 0

    # Categoria (peso 30) — já filtrada na queryset, mas reforça no relatório
    pontos_max += 30
    if item_perdido.categoria_id == item_candidato.categoria_id:
        convergencias.append("Mesma categoria")
        pontos += 30
    else:
        inconsistencias.append("Categoria diferente")

    # Cor (peso 25)
    pontos_max += 25
    if item_perdido.cor_id == item_candidato.cor_id:
        convergencias.append("Mesma cor")
        pontos += 25
    else:
        inconsistencias.append(
            f"Cor divergente ({item_perdido.cor} x {item_candidato.cor})"
        )

    # Similaridade textual da descrição (peso 45)
    pontos_max += 45
    sim = _similaridade_texto(item_perdido.descricao, item_candidato.descricao)
    pontos += round(sim * 45)
    if sim >= 0.5:
        convergencias.append("Descrição textual semelhante")
    else:
        inconsistencias.append("Descrição textual pouco semelhante")

    score = round((pontos / pontos_max) * 100)

    return {
        "item_candidato_id": item_candidato.id,
        "score": score,
        "convergencias": convergencias,
        "inconsistencias": inconsistencias,
    }


def gerar_parecer(analise: Analise) -> Parecer:
    """
    Gera (ou atualiza) o Parecer de uma Análise, comparando o item do
    reporte perdido com todos os itens candidatos disponíveis no estoque.
    """
    item_perdido = analise.reporte.item

    candidatos = Item.objects.filter(
        status=Item.Status.NO_ESTOQUE,
        categoria=item_perdido.categoria,
    )

    resultados = [
        comparar_itens(item_perdido, candidato) for candidato in candidatos
    ]

    resultados.sort(
        key=lambda r: r["score"],
        reverse=True,
    )

    if resultados:
        score_final = resultados[0]["score"]

        if score_final >= 70:
            recomendacao = (
                f"Alta probabilidade de correspondência com o item "
                f"#{resultados[0]['item_candidato_id']}."
            )

        elif score_final >= 40:
            recomendacao = (
                "Correspondência possível. "
                "Recomenda-se análise manual."
            )

        else:
            recomendacao = (
                "Nenhum candidato apresentou "
                "correspondência satisfatória."
            )

    else:
        score_final = 0
        recomendacao = (
            "Nenhum item disponível para comparação."
        )

    parecer, _ = Parecer.objects.update_or_create(
        analise=analise,
        defaults={
            "score_confianca": score_final,
            "convergencias": resultados,
            "inconsistencias": [],
            "recomendacao": recomendacao,
        }
    )

    return parecer
        