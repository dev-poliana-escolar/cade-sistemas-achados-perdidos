from django.db import models
from django.contrib.auth.models import User

from apps.items.models import Item


class Reporte(models.Model):

    class Tipo(models.TextChoices):
        ENCONTRADO = "ENCONTRADO", "Encontrado"
        PERDIDO = "PERDIDO", "Perdido"

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reportes"
    )

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="reportes",
    )

    tipo = models.CharField(
        max_length=15,
        choices=Tipo.choices
    )

    data = models.DateTimeField()

    local = models.CharField(
        max_length=200
    )

    observacoes = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-data"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.item}"