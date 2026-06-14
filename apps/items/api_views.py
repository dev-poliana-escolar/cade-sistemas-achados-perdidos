from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.items.models import Item


@login_required
def api_item_detail(request, pk):
    """
    Retorna um item em JSON.
    """

    item = get_object_or_404(Item, pk=pk)

    return JsonResponse(
        {
            "id": item.id,
            "categoria": item.categoria,
            "descricao": item.descricao,
            "cor": item.cor,
            "local_encontrado": item.local_encontrado,
            "status": item.status,
            "dados_sensiveis": item.dados_sensiveis,
            "cadastrado_por_id": item.cadastrado_por_id,
            "data_encontro": str(item.data_encontro),
        }
    )

