from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from apps.analysis.models import Analise, Parecer
from apps.analysis.services import excluir_analise, restaurar_analise
from apps.category.models import Categoria
from apps.color.models import Cor
from apps.items.models import Item
from apps.report.models import Reporte


class ExclusaoAnaliseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(username="admin", is_staff=True)
        cls.categoria = Categoria.objects.create(nome="Eletrônicos")
        cls.cor = Cor.objects.create(nome="Preto")
        cls.item = Item.objects.create(
            categoria=cls.categoria,
            cor=cls.cor,
            descricao="Celular preto",
            status=Item.Status.PERDIDO,
        )
        cls.reporte = Reporte.objects.create(
            usuario=cls.usuario,
            item=cls.item,
            tipo=Reporte.Tipo.PERDIDO,
            data=timezone.now(),
            local="Biblioteca",
        )
        cls.analise = Analise.objects.create(
            reporte=cls.reporte,
            administrador=cls.usuario,
            justificativa="Análise de teste",
        )
        cls.parecer = Parecer.objects.create(
            analise=cls.analise,
            score_correspondencia=50,
            convergencias=[],
            inconsistencias=[],
            recomendacao="Revisão manual.",
        )

    def test_excluir_mantem_registro_e_relacoes_fora_da_consulta_ativa(self):
        analise_excluida = excluir_analise(self.analise.pk)

        self.assertIsNotNone(analise_excluida.data_exclusao)
        self.assertFalse(Analise.objects.filter(pk=self.analise.pk).exists())
        self.assertTrue(Analise.all_objects.filter(pk=self.analise.pk).exists())
        self.assertTrue(Reporte.objects.filter(pk=self.reporte.pk).exists())
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Parecer.objects.filter(pk=self.parecer.pk).exists())

    def test_excluir_novamente_preserva_data_original(self):
        primeira_exclusao = excluir_analise(self.analise.pk)
        data_exclusao_original = primeira_exclusao.data_exclusao

        segunda_exclusao = excluir_analise(self.analise.pk)

        self.assertEqual(segunda_exclusao.data_exclusao, data_exclusao_original)

    def test_restaurar_recoloca_analise_na_consulta_ativa(self):
        excluir_analise(self.analise.pk)

        analise_restaurada = restaurar_analise(self.analise.pk)

        self.assertIsNone(analise_restaurada.data_exclusao)
        self.assertTrue(Analise.objects.filter(pk=self.analise.pk).exists())

    def test_staff_pode_excluir_por_post_e_analise_sai_da_listagem(self):
        self.client.force_login(self.usuario)

        response = self.client.post(
            reverse("analysis:delete", args=[self.analise.pk])
        )

        self.assertRedirects(response, reverse("analysis:pending_reports"))
        self.assertFalse(Analise.objects.filter(pk=self.analise.pk).exists())
        self.assertTrue(Analise.all_objects.filter(pk=self.analise.pk).exists())

        response = self.client.get(reverse("analysis:pending_reports"))
        self.assertNotContains(response, f"Excluir análise")
        self.assertNotIn(self.reporte, response.context["analise_feita"])

    def test_delete_nao_aceita_get(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse("analysis:delete", args=[self.analise.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Analise.objects.filter(pk=self.analise.pk).exists())

    def test_usuario_nao_staff_nao_pode_excluir(self):
        usuario = User.objects.create_user(username="usuario")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("analysis:delete", args=[self.analise.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Analise.objects.filter(pk=self.analise.pk).exists())

    def test_staff_pode_ver_e_recuperar_analise_excluida(self):
        self.client.force_login(self.usuario)
        excluir_analise(self.analise.pk)

        response = self.client.get(
            reverse("analysis:pending_reports"),
            {"show": "deleted"},
        )

        self.assertContains(response, "Análises excluídas")
        self.assertContains(response, "Recuperar análise")
        self.assertIn(self.reporte, response.context["analise_excluida"])
        self.assertEqual(
            self.client.get(
                reverse("analysis:view", args=[self.reporte.pk])
            ).status_code,
            200,
        )

        response = self.client.post(
            reverse("analysis:restore", args=[self.analise.pk])
        )

        self.assertRedirects(response, reverse("analysis:pending_reports"))
        self.assertTrue(Analise.objects.filter(pk=self.analise.pk).exists())

    def test_recuperacao_exige_post_e_usuario_staff(self):
        excluir_analise(self.analise.pk)
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse("analysis:restore", args=[self.analise.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertFalse(Analise.objects.filter(pk=self.analise.pk).exists())

        usuario = User.objects.create_user(username="usuario")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("analysis:restore", args=[self.analise.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Analise.objects.filter(pk=self.analise.pk).exists())
