from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    """
    Modelo de Item encontrado no campus.
    Controla o ciclo de vida de itens achados até sua devolução ou doação.
    """

    class StatusChoices(models.TextChoices):
        """Estados possíveis de um item no sistema."""
        PENDENTE = "PENDENTE", "Pendente - Aguardando entrega na COAPAC"
        VALIDO = "VALIDO", "Válido - Aprovado para publicação"
        ARMAZENADO = "ARMAZENADO", "Armazenado"
        DISPONIVEL_PARA_DOACAO = "DISPONIVEL_PARA_DOACAO", "Disponível para Doação"
        ENTREGUE = "ENTREGUE", "Entregue"
        SORTEADO_AGUARDANDO_ENTREGA = "SORTEADO_AGUARDANDO_ENTREGA", "Sorteado - Aguardando Entrega"
        DOADO = "DOADO", "Doado"
        CANCELADO = "CANCELADO", "Cancelado"

    # Campos básicos
    descricao = models.TextField(max_length=500)
    imagem = models.ImageField(upload_to="items/%Y/%m/%d/")
    cor = models.CharField(max_length=100)
    local_encontrado = models.CharField(max_length=255)
    observacoes = models.TextField(blank=True, null=True)

    # Status e auditoria
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE
    )
    dados_sensiveis = models.BooleanField(default=False)

    # Relacionamentos e datas
    cadastrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="itens_cadastrados"
    )
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_validados"
    )

    data_encontro = models.DateTimeField()
    data_despacho = models.DateTimeField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Item #{self.id} - {self.descricao[:50]}"
