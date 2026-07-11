from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from apps.report.models import Reporte
from apps.analysis.forms import AnaliseForm
from apps.items.models import Item
from django.contrib import messages 


# Create your views here.

@login_required
@staff_member_required
def dashboard(request):

    reportes_perdidos = Reporte.objects.filter(
        tipo=Reporte.Tipo.PERDIDO
    )

    entregas_pendentes = Reporte.objects.filter(
        tipo=Reporte.Tipo.ENCONTRADO,
        item__status=Item.Status.AGUARDANDO_ENTREGA,
    )

    return render(
        request,
        "admin/dashboard.html",
        {
            "reportes_perdidos": reportes_perdidos,
            "entregas_pendentes": entregas_pendentes,
        },
    )


@login_required
@staff_member_required
def pending_reports(request):
   """
   Lista todos os reportes de tipo PERDIDO 
   """
   reportes_itens_perdidos = Reporte.objects.filter(tipo=Reporte.Tipo.PERDIDO)

   return render (request, 'analysis/pending_reports.html', {
      "title": "Reportes pendentes de análise",
      'reportes':reportes_itens_perdidos
   })


@login_required
@staff_member_required
def pending_deliveries(request):
   """
   Lista todos os reportes do tipo ENCONTRADO
   """

   reportes_itens_encontrados = Reporte.objects.filter(
      tipo=Reporte.Tipo.ENCONTRADO,
      item__status=Item.Status.AGUARDANDO_ENTREGA,
   )
   return render (request, 'analysis/pending_deliveries.html',{
        "title": "Entregas pendentes",
        "reportes": reportes_itens_encontrados,
      },
   )

@login_required
@staff_member_required
def confirm_delivered(request, id):
   """
   Confirma que o item de um reporte 'Encontrado' foi entregue fisicamente no estoque
   """
   reporte = get_object_or_404(Reporte,id=id)
  

   if reporte.tipo != Reporte.Tipo.ENCONTRADO:
      messages.error(request,"Este reporte não é do tipo encontrado.")
      return redirect("analysis:dashboard")

   if reporte.item.status != Item.Status.AGUARDANDO_ENTREGA:
      messages.error(
         request,
         "Este item já foi confirmado ou não está aguardando entrega."
      )
      return redirect("analysis:dashboard")

   reporte.item.status = Item.Status.NO_ESTOQUE
   reporte.item.save()

   messages.success(
      request,
      "Entrega confirmada com sucesso."
   )

   return redirect("analysis:dashboard")



# @login_required
# @staff_member_required
# def create_analysis(request, reporte_id):
#    """
#    Inicia uma analise de um reporte
#    """

#    reporte = get_object_or_404(
#       Reporte,
#       id=reporte_id
#    )

#    itens_encontrados = Reporte.objects.filter(
#       tipo=Reporte.Tipo.ENCONTRADO,
#       item__status=Reporte.Status.NO_ESTOQUE,
#    )

#    if request.method == "POST":
#       form= AnaliseForm(request.POST) 

#       if form.is_valid():
#          analise = form.save(commit=False)
#          analise.administrador = request.user
#          analise.save()
#    else:
#       form = AnaliseForm()

#    return render(request, 'analise/create.html', {'form': form})





   

    
