from django.db import models
from apps.report.models import Reporte
from django.contrib.auth.models import User
# Create your models here.

class Analise(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CORRESPONDENCIA_ENCONTRADA = "CORRESPONDENCIA_ENCONTRADA", "Correspondência Encontrada"
        SEM_CORRESPONDENCIA = "SEM_CORRESPONDENCIA", "Sem Correspondência"
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='analises'
    )

    administrador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='analises'
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    justificativa = models.TextField()

    data_analise = models.DateTimeField(auto_now_add=True)
