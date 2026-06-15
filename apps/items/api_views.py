from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.items.models import Item
from apps.items.forms import ItemForm


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

@login_required
def api_item_create(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Método não permitido"},
            status=405
        )

    form = ItemForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                "error": "Dados inválidos",
                "details": form.errors,
            },
            status=400,
        )

    item = form.save(commit=False)
    item.cadastrado_por = request.user
    item.save()

    return JsonResponse(
        {
            "id": item.id,
            "status": item.status,
        },
        status=201,
    )

@login_required
def api_item_cancel(request, pk):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Método não permitido"},
            status=405,
        )

    item = get_object_or_404(
        Item,
        pk=pk,
        cadastrado_por=request.user,
    )

    if item.status != Item.Status.PENDENTE:
        return JsonResponse(
            {
                "error": (
                    "Este item não pode "
                    "ser cancelado."
                )
            },
            status=400,
        )

    item.status = Item.Status.CANCELADO
    item.save()

    return JsonResponse(
        {
            "id": item.id,
            "status": item.status,
        }
    )