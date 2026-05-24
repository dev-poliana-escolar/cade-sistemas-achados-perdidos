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
            Item.Status.VALIDO,
            Item.Status.ARMAZENADO,
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
def my_items(request):
    """
    Lista dos itens cadastrados pelo usuário logado.
    """

    itens = Item.objects.filter(
        cadastrado_por=request.user
    )

    return render(
        request,
        "items/my_items.html",
        {
            "title": "Meus Cadastros",
            "itens": itens,
        },
    )


@login_required
def item_create(request):
    """
    Cadastro de novo item encontrado.
    """

    if request.method == "POST":

        form = ItemForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.cadastrado_por = request.user
            item.save()

            messages.success(
                request,
                (
                    "Item cadastrado com sucesso! "
                    "Entregue o item fisicamente "
                    "na COAPAC para validação."
                ),
            )

            return redirect(
                reverse("items:my_items")
            )

    else:
        form = ItemForm()

    return render(
        request,
        "items/create.html",
        {
            "title": "Cadastrar Item",
            "form": form,
        },
    )


@login_required
def item_edit(request, pk):
    """
    Permite edição de itens pendentes.
    """

    item = get_object_or_404(
        Item,
        pk=pk,
        cadastrado_por=request.user,
    )

    if item.status != Item.Status.PENDENTE:

        messages.error(
            request,
            (
                "Este item não pode mais "
                "ser editado."
            ),
        )

        return redirect(
            reverse("items:my_items")
        )

    if request.method == "POST":

        form = ItemForm(
            request.POST,
            request.FILES,
            instance=item,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Item atualizado com sucesso."
            )

            return redirect(
                reverse("items:my_items")
            )

    else:
        form = ItemForm(instance=item)

    return render(
        request,
        "items/edit.html",
        {
            "title": "Editar Item",
            "form": form,
            "item": item,
        },
    )


@login_required
def item_cancel(request, pk):
    """
    Cancela um item pendente.
    """

    item = get_object_or_404(
        Item,
        pk=pk,
        cadastrado_por=request.user,
    )

    if item.status != Item.Status.PENDENTE:

        messages.error(
            request,
            "Este item não pode ser cancelado."
        )

        return redirect(
            reverse("items:my_items")
        )

    if request.method == "POST":

        item.status = Item.Status.CANCELADO

        item.save()

        messages.success(
            request,
            "Item cancelado com sucesso."
        )

        return redirect(
            reverse("items:my_items")
        )

    return render(
        request,
        "items/cancel_confirm.html",
        {
            "title": "Cancelar Item",
            "item": item,
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
            reverse("items:found_items")
        )

    return render(
        request,
        "items/delete.html",
        {
            "title": "Excluir Item",
            "item": item,
        },
    )