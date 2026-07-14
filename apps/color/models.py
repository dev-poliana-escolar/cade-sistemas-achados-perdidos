from django.db import models


class Cor(models.Model):
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome"
    )

    class Meta:
        verbose_name = "Cor"
        verbose_name_plural = "Cores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
