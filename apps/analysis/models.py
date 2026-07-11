from django.db import models
from apps.report.models import Reporte
from django.contrib.auth.models import User
from apps.items.models import Item
# Create your models here.

class Analise(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        EM_ANALISE = "EM_ANALISE", "Em Análise"
        CORRESPONDENCIA_ENCONTRADA = "CORRESPONDENCIA_ENCONTRADA", "Correspondência Encontrada"
        SEM_CORRESPONDENCIA = "SEM_CORRESPONDENCIA", "Sem Correspondência"
    
    reporte = models.OneToOneField(
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

    item_encontrado = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="analises_como_encontrado"
    )

    justificativa = models.TextField()

    data_analise = models.DateTimeField(auto_now_add=True)
