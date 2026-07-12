from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from apps.report.models import Reporte
from apps.analysis.forms import AnaliseForm
from apps.analysis.models import Analise
from apps.items.models import Item
from django.contrib import messages 
from apps.analysis.services import gerar_parecer
from apps.analysis import ai as analysis_ai


# Create your views here.

@login_required
@staff_member_required
def dashboard(request):

    reportes_perdidos = Reporte.objects.filter(
        tipo=Reporte.Tipo.PERDIDO,
        analises__isnull=True
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
   reportes_itens_perdidos = Reporte.objects.filter(
      tipo=Reporte.Tipo.PERDIDO
   )
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



@login_required
@staff_member_required
def create_analysis(request, id):
   reporte = get_object_or_404(
      Reporte, id=id, tipo=Reporte.Tipo.PERDIDO,
   )

   analise, created = Analise.objects.get_or_create(
      reporte=reporte,
      administrador=request.user,
      defaults={"status": Analise.Status.EM_ANALISE},
   )

   itens_encontrados = Item.objects.filter(
      status=Item.Status.NO_ESTOQUE,
      categoria=reporte.item.categoria,
   )

   parecer = getattr(analise, "parecer", None)

   if request.method == "POST":
      action = request.POST.get("action")

      if action == "gerar_parecer":
         parecer = gerar_parecer(analise)
         messages.success(request, "Parecer gerado com sucesso.")
         return redirect("analysis:create", id=reporte.id)
      if action == "gerar_parecer_ia":
         try:
            parecer = analysis_ai.gerar_parecer_ia(analise)
            messages.success(request, "Parecer gerado com IA com sucesso.")
            return redirect("analysis:create", id=reporte.id)
         except RuntimeError:
            parecer = gerar_parecer(analise)
            
            messages.warning(
               request,
               (
                     "A IA não pôde ser utilizada. "
                     "Foi gerado um parecer heurístico."
               ),
            )
            return redirect("analysis:create", id=reporte.id)

      form = AnaliseForm(request.POST, instance=analise)
      form.fields["item_encontrado"].queryset = itens_encontrados

      if form.is_valid():
         analise = form.save(commit=False)
         analise.status = (
               Analise.Status.CORRESPONDENCIA_ENCONTRADA
               if analise.item_encontrado
               else Analise.Status.SEM_CORRESPONDENCIA
         )
         analise.save()
         messages.success(request, "Análise finalizada com sucesso.")
         return redirect("analysis:dashboard")
   else:
      form = AnaliseForm(instance=analise)
      form.fields["item_encontrado"].queryset = itens_encontrados

   comparacoes = []

   if parecer:

      itens = {
         item.id: item
         for item in itens_encontrados
      }

      for resultado in parecer.convergencias:
         
         resultado["item"] = itens[
            resultado["item_candidato_id"]
         ]

         comparacoes.append(resultado)

   return render(
      request,
      "analysis/create.html",
      {
         "title": "Analisar reporte",
         "form": form,
         "reporte": reporte,
         "itens_encontrados": itens_encontrados,
         "parecer": parecer,
         "comparacoes": comparacoes,
      },
   )