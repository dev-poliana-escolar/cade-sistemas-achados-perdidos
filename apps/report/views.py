from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.items.forms import ItemForm
from apps.report.forms import ReporteForm
from apps.report.models import Reporte
from apps.items.models import Item


@login_required
def my_reports(request):
    """
    Lista os reportes realizados pelo usuário autenticado.
    """

    reportes= Reporte.objects.filter(usuario=request.user)

    return render( request, "report/my_reports.html", {"reportes": reportes})


@login_required
def report_create(request):
    """
    Cadastro de um novo reporte.

    - Reporte ENCONTRADO:
        cria um Item com status AGUARDANDO_ENTREGA
        e o associa ao Reporte.

    - Reporte PERDIDO:
        cria um Item com status PERDIDO
        e o associa ao Reporte.
    """

    if request.method == "POST":
        

        reporte_form = ReporteForm(request.POST)
        item_form = ItemForm(request.POST, request.FILES)

        tipo = request.POST.get("tipo")

        if reporte_form.is_valid() and item_form.is_valid():
            print("VALIDOU")
            with transaction.atomic():

                item = item_form.save(commit=False)

                if tipo == Reporte.Tipo.PERDIDO:
                    item.status = Item.Status.PERDIDO
                else:
                    item.status = Item.Status.AGUARDANDO_ENTREGA

                item.save()

                reporte = reporte_form.save(commit=False)
                reporte.usuario = request.user
                reporte.item = item
                reporte.save()
                print('deu')

                

            if tipo == Reporte.Tipo.PERDIDO:
                messages.success(
                    request,
                    (
                        "Reporte de perda registrado com sucesso! "
                        "Nossa equipe analisará a solicitação."
                    ),
                )
            else:
                messages.success(
                    request,
                    (
                        "Reporte cadastrado com sucesso! "
                        "Entregue o item fisicamente "
                        "na COAPAC para validação."
                    ),
                )
            return redirect(reverse("report:my_reports"))

    else: 
        reporte_form = ReporteForm()
        item_form = ItemForm()
        

    return render(
        request,
        "report/create.html",
        {
            "title": "Novo Reporte",
            "reporte_form": reporte_form,
            "item_form": item_form,
        },
    )

@login_required
def report_delete(request, id):
    """
    Deleta um reporte e o item associado a ele.
    """

    reporte = get_object_or_404(
        Reporte,
        id=id,
        usuario=request.user,
    )

    if request.method=="POST":
        if reporte.item.status not in [Item.Status.PERDIDO, Item.Status.AGUARDANDO_ENTREGA]:
            messages.error(
                request,
                (
                    "Não é possível deletar este reporte. "
                    "O item associado já foi entregue ou doado."
                ),
            )
            return redirect(reverse("report:my_reports"))
    
       
        reporte.item.delete() 
        messages.success(
            request,
            "Reporte deletado com sucesso!"
        )

        return redirect(reverse("report:my_reports"))
        
   
    return render(
        request,
        "report/delete.html",
        {
            "title": "Deletar Reporte",
            "reporte": reporte,
        },
    )
    