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

class Parecer(models.Model):
    """
    Resultado da comparação automática entre o item de um reporte 
    PERDIDO e os itens candidatos no estoque.
    """

    analise = models.OneToOneField(
        Analise,
        on_delete=models.CASCADE,
        related_name="parecer"
    )

    score_correspondencia = models.PositiveSmallIntegerField(
        help_text="Score de 0 a 100 indicando o grau de confiança na melhor correspondência encontrada."
    )

    convergencias = models.JSONField(
        default=dict,
        help_text="Pontos em que o item candidato bate com a descrição do item perdido."
    )

    inconsistencias = models.JSONField(
        default=dict,
        help_text="Pontos em que o item candidato diverge da descrição do item perdido."
    )

    recomendacao = models.TextField(
        help_text="Texto legível resumindo a sugestão do sistema para o admin."
    )

    # Campos que só farão sentido de fato na fase 2 (IA)
    prompt = models.TextField(blank=True, null=True)
    data_prompt = models.DateTimeField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parecer"
        verbose_name_plural = "Pareceres"

    def __str__(self):
        return f"Parecer da análise #{self.analise_id} (score {self.score_correspondencia})"
