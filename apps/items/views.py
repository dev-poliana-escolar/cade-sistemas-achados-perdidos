from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.items.forms import ItemForm
from apps.items.models import Item


@login_required
def found_items(request):
    """
    Lista pública de itens encontrados.
    Exibe apenas itens validados ou armazenados.
    """

    itens = Item.objects.filter(
        status__in=[
            Item.Status.AGUARDANDO_ENTREGA,
            Item.Status.NO_ESTOQUE,
        ]
    )

    return render(
        request,
        "items/found_items.html",
        {
            "title": "Itens Encontrados",
            "itens": itens,
        },
    )


@login_required
def donation_items(request):
    """
    Lista de itens disponíveis para doação.
    """

    itens = Item.objects.filter(
        status=Item.Status.DISPONIVEL_PARA_DOACAO
    )

    return render(
        request,
        "items/donation_items.html",
        {
            "title": "Itens para Doação",
            "itens": itens,
        },
    )


@login_required
def item_delete(request, pk):
    """
    Exclusão administrativa de itens.
    """

    if not request.user.is_staff:

        messages.error(
            request,
            (
                "Você não possui permissão "
                "para excluir itens."
            ),
        )

        return redirect(
            reverse("items:found_items")
        )

    item = get_object_or_404(
        Item,
        pk=pk,
    )

    if request.method == "POST":

        item.delete()

        messages.success(
            request,
            "Item excluído com sucesso."
        )

        return redirect(
            reverse("items:admin_items")
        )

    return render(
        request,
        "items/delete.html",
        {
            "title": "Excluir Item",
            "item": item,
        },
    )


