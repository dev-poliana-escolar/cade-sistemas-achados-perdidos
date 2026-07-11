from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Reporte


# Create your views here.

@login_required
@staff_member_required
def pending_reports(request):
   """
   Lista todos os reportes de status perdido 
   """
   reportes_itens_perdidos = Reporte.objects.filter(tipo='PERDIDO')

   return render (request, 'analysis/pending_reports.html', {
      'reportes':reportes_itens_perdidos
   })



   

    
