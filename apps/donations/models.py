from django.db import models

from django.contrib.auth.models import User
from apps.items.models import Item


class SessaoDoacao(models.Model):
    admin_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sessoes_doacao'
    )
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sessão de Doação'
        verbose_name_plural = 'Sessões de Doação'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'Sessão de Doação #{self.pk} — {"Ativa" if self.ativa else "Encerrada"}'


class InteresseDoacao(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interesses_doacao'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='interesses'
    )
    sessao = models.ForeignKey(
        SessaoDoacao,
        on_delete=models.CASCADE,
        related_name='interesses',
        null=True,
        blank=True
    )
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Interesse em Doação'
        verbose_name_plural = 'Interesses em Doação'
        unique_together = ('usuario', 'item')

    def __str__(self):
        return f'{self.usuario} → {self.item}'


class Doacao(models.Model):
    interesse = models.OneToOneField(
        InteresseDoacao,
        on_delete=models.CASCADE,
        related_name='doacao'
    )
    sessao = models.ForeignKey(
        SessaoDoacao,
        on_delete=models.CASCADE,
        related_name='doacoes'
    )
    data_sorteio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data_sorteio']

    def __str__(self):
        return f'Doação de {self.interesse.item} para {self.interesse.usuario}'
