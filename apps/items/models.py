from django.db import models
from django.contrib.auth.models import User
from apps.category.models import Categoria
from apps.color.models import Cor


class Item(models.Model):

    class Status(models.TextChoices):
        PERDIDO = "PERDIDO", "Perdido"
        AGUARDANDO_ENTREGA = "AGUARDANDO_ENTREGA", "Aguardando entrega"
        NO_ESTOQUE = "NO_ESTOQUE", "No estoque"
        DISPONIVEL_PARA_DOACAO = "DISPONIVEL_PARA_DOACAO", "Disponível para doação"
        DEVOLVIDO = "DEVOLVIDO", "Devolvido"
        DOADO = "DOADO", "Doado"

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
    )

    cor = models.ForeignKey(
        Cor,
        on_delete=models.PROTECT
    )

    descricao = models.TextField()

    imagem = models.ImageField(
        upload_to="items/",
        blank=True,
        null=True
    )

    dados_sensiveis = models.BooleanField(default=False)


    data_despacho = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.categoria} - {self.descricao} ({self.cor})"
   