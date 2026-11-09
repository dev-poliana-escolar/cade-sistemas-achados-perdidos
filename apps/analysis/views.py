from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from apps.report.models import Reporte
from apps.analysis.forms import AnaliseForm
from apps.analysis.models import Analise
from apps.items.models import Item
from django.contrib import messages 
from apps.analysis.services import editar_analise, gerar_parecer, simular_novo_parecer_ia
from apps.analysis import ai as analysis_ai
from .forms import EditarAnaliseForm

# Create your views here.
@login_required
@staff_member_required
def edit_analysis(request, id):
   analise = get_object_or_404(Analise, id=id)
   session_key = f"preview_parecer_{analise.id}"
   preview_parecer = None

   if request.method == "POST":
      action = request.POST.get("action")
      form = EditarAnaliseForm(request.POST, instance=analise)

      if action == "regerar_parecer":
         try:
               preview_parecer = simular_novo_parecer_ia(analise)
               request.session[session_key] = preview_parecer
               messages.info(
                  request,
                  "Novo parecer gerado para pré-visualização. "
                  "Clique em 'Salvar Alterações' para confirmar.",
               )
         except RuntimeError as e:
               messages.error(request, str(e))
               preview_parecer = request.session.get(session_key)
      elif action == "salvar":
            preview_parecer = request.session.get(session_key)
            if form.is_valid():
               try:
                  editar_analise(
                        analise_id=analise.id,
                        status=form.cleaned_data["status"],
                        justificativa=form.cleaned_data["justificativa"],
                        item_encontrado=form.cleaned_data.get("item_encontrado"),
                        novo_parecer_dados=preview_parecer,
                  )
                  request.session.pop(session_key, None)
                  messages.success(request, "Análise atualizada com sucesso.")
                  return redirect("analysis:pending_reports")

               except ValidationError as e:
                  messages.error(request, e.message)
               except RuntimeError as e:
                  messages.error(request, str(e))
   else:
      # Ao abrir a página do zero (GET), descarta qualquer prévia não salva
      request.session.pop(session_key, None)
      form = EditarAnaliseForm(instance=analise)

   parecer_exibido = preview_parecer or getattr(analise, "parecer", None)

   return render(
      request,
      "analysis/edit.html",
      {
         "title": f"Editar Análise #{analise.id}",
         "form": form,
         "analise": analise,
         "parecer": parecer_exibido,
         "is_preview": preview_parecer is not None,
      },
   )

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
    Lista todos os reportes de tipo PERDIDO com ANALISE pendente ou feita.
    """
    analise_perda_pendente = Reporte.objects.filter(
        tipo=Reporte.Tipo.PERDIDO,
        analises__isnull=True
    ).select_related("item", "item__categoria")

    analise_perda_feita = Reporte.objects.filter(
        tipo=Reporte.Tipo.PERDIDO,
        analises__isnull=False
    ).select_related("item", "item__categoria").prefetch_related("analises").distinct()

    return render(request, 'analysis/pending_reports.html', {
        "title": "Reportes de perda",
        "analise_pendente": analise_perda_pendente,
        "analise_feita": analise_perda_feita,
    })
    
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
      defaults={
         "administrador": request.user,
         "status": Analise.Status.EM_ANALISE
         },
   )

   itens_encontrados = Item.objects.filter(
      status=Item.Status.NO_ESTOQUE
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
         return redirect("analysis:pending_reports")
   else:
      form = AnaliseForm(instance=analise)
      form.fields["item_encontrado"].queryset = itens_encontrados

   comparacoes = []

   if parecer:
      ids_avaliados = [
         c["item_candidato_id"] 
         for c in parecer.convergencias
      ]

      itens_avaliados = {
         item.id: item
         for item in Item.objects.filter(id__in=ids_avaliados)
      }

      for resultado in parecer.convergencias:
         item = itens_avaliados.get(resultado["item_candidato_id"])

         if item is None:
            continue

         resultado["item"] = item
         comparacoes.append(resultado)

   comparacoes_por_item = {
      comparacao["item"].id: comparacao
      for comparacao in comparacoes
   }
   itens_comparacoes = [
      {
         "item": item,
         "comparacao": comparacoes_por_item.get(item.id),
      }
      for item in itens_encontrados
   ]

   return render(
      request,
      "analysis/create.html",
      {
         "title": "Analisar reporte",
         "form": form,
         "reporte": reporte,
         "itens_encontrados": itens_encontrados,
         "parecer": parecer,
         "comparacoes_por_item": comparacoes_por_item,
         "itens_comparacoes": itens_comparacoes, 
      },
   )

@login_required
@staff_member_required
def view_analysis(request, reporte_id):
   """
   Exibe a análise de um reporte específico.
   """
   try:
      analise = Analise.objects.get(
         reporte=reporte_id
         )
      return render(
         request,
         "analysis/view.html",
         {
            "title": "Analise do reporte",
            "analise": analise,
            "parecer": getattr(analise,"parecer",None), #impede o lançamento de exceção Parecer.DoesNotExist.
         }
      )
   except Analise.DoesNotExist:
      messages.error(request, "Análise não encontrada para este reporte.")
      return redirect("analysis:dashboard")