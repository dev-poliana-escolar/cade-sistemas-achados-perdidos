from django.db import models

from django.contrib.auth.models import User
from apps.items.models import Item


class Reivindicacao(models.Model):

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANALISE = 'EM_ANALISE', 'Em Análise'
        APROVADA = 'APROVADA', 'Aprovada'
        NEGADA = 'NEGADA', 'Negada'

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='reivindicacoes'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reivindicacoes'
    )
    motivo = models.TextField()
    data_perda = models.DateField()
    local_perda = models.CharField(max_length=200)
    caracteristicas_especificas = models.TextField()
    evidencia = models.FileField(upload_to='evidencias/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )
    justificativa_admin = models.TextField(blank=True)
    data_decisao = models.DateTimeField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reivindicação'
        verbose_name_plural = 'Reivindicações'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Reivindicação de {self.usuario} para {self.item}'


class ParecerIA(models.Model):
    reivindicacao = models.OneToOneField(
        Reivindicacao,
        on_delete=models.CASCADE,
        related_name='parecer_ia'
    )
    score_confianca = models.FloatField()
    convergencias = models.JSONField(default=list)
    inconsistencias = models.JSONField(default=list)
    recomendacao = models.TextField()
    perguntas_sugeridas = models.JSONField(default=list)
    prompt_utilizado = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Parecer da IA'
        verbose_name_plural = 'Pareceres da IA'

    def __str__(self):
        return f'Parecer IA — Score: {self.score_confianca}% ({self.reivindicacao})'