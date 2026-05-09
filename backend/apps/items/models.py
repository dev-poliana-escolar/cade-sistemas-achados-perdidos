from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    """
    Representa um item encontrado no campus.

    Controla o ciclo de vida de objetos cadastrados no sistema,
    desde o registro inicial até devolução, doação ou cancelamento.
    """

    class Status(models.TextChoices):
        """
        Estados possíveis de um item no sistema.
        """
        PENDENTE = 'PENDENTE', 'Pendente'
        VALIDO = 'VALIDO', 'Válido'
        ARMAZENADO = 'ARMAZENADO', 'Armazenado'
        DISPONIVEL_PARA_DOACAO = 'DISPONIVEL_PARA_DOACAO', 'Disponível para Doação'
        SORTEADO_AGUARDANDO_ENTREGA = 'SORTEADO_AGUARDANDO_ENTREGA', 'Sorteado - Aguardando Entrega'
        REIVINDICADO_AGUARDANDO_ENTREGA = 'REIVINDICADO_AGUARDANDO_ENTREGA', 'Reivindicado - Aguardando Entrega'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        DOADO = 'DOADO', 'Doado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    class Categoria(models.TextChoices):
        """
        Categorias disponíveis para classificação dos itens.
        """
        ELETRONICO = 'ELETRONICO', 'Eletrônico'
        DOCUMENTO = 'DOCUMENTO', 'Documento'
        VESTUARIO = 'VESTUARIO', 'Vestuário'
        ACESSORIO = 'ACESSORIO', 'Acessório'
        GARRAFA = 'GARRAFA', 'Garrafa'
        MATERIAL_ESCOLAR = 'MATERIAL_ESCOLAR', 'Material Escolar'
        OUTRO = 'OUTRO', 'Outro'

    imagem = models.ImageField(
        upload_to='items/', 
        blank=True, 
        null=True
    )

    categoria = models.CharField(
        max_length=20, 
        choices=Categoria.choices
    )

    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=50)
    local_encontrado = models.CharField(max_length=200)
    observacoes = models.TextField(blank=True)
    dados_sensiveis = models.BooleanField(default=False)

    status = models.CharField(
        max_length=35,
        choices=Status.choices,
        default=Status.PENDENTE
    )

    cadastrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name='itens_cadastrados'
    )
    
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_validados'
    )
    
    data_encontro = models.DateField()
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_despacho = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['-data_cadastro']

    def __str__(self):
        return f'{self.get_categoria_display()} - {self.cor} ({self.get_status_display()})'
