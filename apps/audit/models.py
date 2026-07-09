from django.db import models

from django.contrib.auth.models import User


class Auditoria(models.Model):

    class Origem(models.TextChoices):
        USUARIO = 'USUARIO', 'Usuário'
        SISTEMA = 'SISTEMA', 'Sistema'

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_auditoria'
    )
    acao = models.CharField(max_length=200)
    origem = models.CharField(
        max_length=10,
        choices=Origem.choices,
        default=Origem.USUARIO
    )
    entidade_tipo = models.CharField(max_length=50)
    entidade_id = models.IntegerField()
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-data_criacao']
        # Impede qualquer alteração após criação (read-only)
        default_permissions = ('view',)

    def __str__(self):
        return f'[{self.data_criacao:%d/%m/%Y %H:%M}] {self.acao} — {self.entidade_tipo} #{self.entidade_id}'

    def save(self, *args, **kwargs):
        # Impede edição após criação
        if self.pk:
            return
        super().save(*args, **kwargs)
