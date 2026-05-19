from django.test import TestCase

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
# IMPORTAÇÃO COMENTADA - SimpleUploadedFile usado apenas se for testar upload de imagem:
# from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

from apps.items.forms import ItemForm
from apps.items.models import Item

User = get_user_model()


class CadastroItemTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="pass1234"
        )

        # IMAGEM COMENTADA PARA USO FUTURO:
        # Valid image: 1x1 PNG pixel in bytes
        # self.valid_png_1x1 = (
        #     b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        #     b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c'
        #     b'c\xf8\x0f\x00\x00\x01\x01\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00'
        #     b'IEND\xaeB`\x82'
        # )
        #
        # self.image_file = SimpleUploadedFile(
        #     name="test.png",
        #     content=self.valid_png_1x1,
        #     content_type="image/png",
        # )

        # Minimal valid data for forms and views
        # data_encontro must be in format YYYY-MM-DD (per forms.DateInput widget)
        self.base_data = {
            "categoria": Item.Categoria.ELETRONICO,
            "cor": "PRETO",
            "descricao": "Caneta encontrada",
            "local_encontrado": "Bloco A",
            "data_encontro": "2020-01-01",
        }

    def test_form_rejects_blank_required_fields(self):
        """
        Critérios de Aceitação 1-4: Validar erros em campos obrigatórios diretamente no formulário.
        """
        data = {
            "categoria": "",
            "cor": "PRETO",
            "descricao": "",
            "local_encontrado": "",
            "data_encontro": "",
        }

        form = ItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("descricao", form.errors)
        self.assertIn("categoria", form.errors)
        self.assertIn("local_encontrado", form.errors)
        self.assertIn("data_encontro", form.errors)

    def test_form_accepts_valid_required_fields(self):
        """
        Critérios de Aceitação 1-4: Validar que o formulário aceita
        descrição, categoria, local e data válidos.
        Imagem é opcional (não testada nesta função).
        """
        data = self.base_data.copy()
        # IMAGEM COMENTADA - Usar SimpleUploadedFile se precisar testar upload futuro:
        # form = ItemForm(data=data, files={"imagem": self.image_file})
        form = ItemForm(data=data, files={})
        
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["descricao"], "Caneta encontrada")
        self.assertEqual(form.cleaned_data["categoria"], Item.Categoria.ELETRONICO)
        self.assertEqual(form.cleaned_data["local_encontrado"], "Bloco A")
        # Comparar data como string para evitar erro de tipo
        self.assertEqual(str(form.cleaned_data["data_encontro"]), "2020-01-01")

    def test_outro_cor_transformed_to_uppercase(self):
        """Teste de transformação de cor 'OUTRA' para maiúscula"""
        data = self.base_data.copy()
        data.update({
            "cor": "OUTRA",
            "outra_cor": "Azul Turquesa",
        })

        # IMAGEM COMENTADA - Para usar: files={"imagem": self.image_file}
        form = ItemForm(data=data, files={})
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["cor"], "AZUL TURQUESA")

    # TESTE COMENTADO - Relacionado a detecção de dados sensíveis:
    # def test_sensitive_detection_forces_dados_sensiveis(self):
    #     data = self.base_data.copy()
    #     # include the keyword 'CPF' and explicitly send dados_sensiveis False
    #     data.update({
    #         "descricao": "Documento com CPF: 000.000.000-00",
    #         "dados_sensiveis": False,
    #     })
    #
    #     form = ItemForm(data=data, files={"imagem": self.image_file})
    #     self.assertTrue(form.is_valid(), msg=form.errors)
    #     # the form's cleaning should set dados_sensiveis to True
    #     self.assertTrue(form.cleaned_data.get("dados_sensiveis", False))

    def test_item_create_view_forces_status_pendente(self):
        """
        Critério de Aceitação: Validar que a criação de item salva
        automaticamente com status PENDENTE.
        """
        self.client.login(username="tester", password="pass1234")

        data = self.base_data.copy()
        data["descricao"] = "Relógio encontrado"

        # IMAGEM COMENTADA - Para usar: files={"imagem": self.image_file}
        response = self.client.post(
            reverse("items:create"),
            data={
                "categoria": data["categoria"],
                "cor": data["cor"],
                "descricao": data["descricao"],
                "local_encontrado": data["local_encontrado"],
                "data_encontro": data["data_encontro"],
            },
            files={},  # files={"imagem": self.image_file}
        )

        # After creation, the user is redirected (302)
        self.assertEqual(response.status_code, 302)

        # The item must exist and have status PENDENTE and be associated with the user
        item = Item.objects.get(descricao="Relógio encontrado", cadastrado_por=self.user)
        self.assertEqual(item.status, Item.Status.PENDENTE)

    def test_edit_and_cancel_blocked_when_status_is_not_pendente(self):
        """
        Validar que edição/cancelamento são BLOQUEADOS se status != PENDENTE
        """
        # create an item owned by user but with status VALIDO
        item = Item.objects.create(
            categoria=Item.Categoria.ELETRONICO,
            cor="PRETO",
            descricao="Fone de ouvido",
            local_encontrado="Sala 1",
            data_encontro=timezone.now().date(),
            cadastrado_por=self.user,
            status=Item.Status.VALIDO,
        )

        self.client.login(username="tester", password="pass1234")

        # attempt to edit (POST)
        edit_url = reverse("items:edit", args=[item.pk])
        response = self.client.post(edit_url, data={
            "categoria": item.categoria,
            "cor": item.cor,
            "descricao": "Alterada",
            "local_encontrado": item.local_encontrado,
            "data_encontro": item.data_encontro.strftime("%Y-%m-%d"),
            # IMAGEM COMENTADA - Para usar: "imagem": self.image_file
        }, follow=True)

        # should be redirected to my_items and show an error message
        self.assertRedirects(response, reverse("items:my_items"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.level_tag == "error" for m in messages))

        # attempt to cancel (POST)
        cancel_url = reverse("items:cancel", args=[item.pk])
        response = self.client.post(cancel_url, follow=True)
        self.assertRedirects(response, reverse("items:my_items"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.level_tag == "error" for m in messages))

    def test_edit_and_cancel_allowed_when_status_is_pendente(self):
        """
        Validar que edição/cancelamento são PERMITIDOS se status == PENDENTE
        """
        # create an item owned by user with status PENDENTE
        item = Item.objects.create(
            categoria=Item.Categoria.ELETRONICO,
            cor="PRETO",
            descricao="Fone de ouvido",
            local_encontrado="Sala 1",
            data_encontro=timezone.now().date(),
            cadastrado_por=self.user,
            status=Item.Status.PENDENTE,
        )

        self.client.login(username="tester", password="pass1234")

        # Test EDIT: attempt to edit (POST)
        edit_url = reverse("items:edit", args=[item.pk])
        response = self.client.post(edit_url, data={
            "categoria": item.categoria,
            "cor": item.cor,
            "descricao": "Alterada com sucesso",
            "local_encontrado": item.local_encontrado,
            "data_encontro": item.data_encontro.strftime("%Y-%m-%d"),
            # IMAGEM COMENTADA - Para usar: "imagem": self.image_file
        }, follow=True)

        # should be redirected to my_items with success message
        self.assertRedirects(response, reverse("items:my_items"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.level_tag == "success" for m in messages))

        # Verify the edit was applied
        item.refresh_from_db()
        self.assertEqual(item.descricao, "Alterada com sucesso")

        # Test CANCEL: create a new PENDENTE item and cancel it
        item2 = Item.objects.create(
            categoria=Item.Categoria.ELETRONICO,
            cor="AZUL",
            descricao="Item a cancelar",
            local_encontrado="Bloco B",
            data_encontro=timezone.now().date(),
            cadastrado_por=self.user,
            status=Item.Status.PENDENTE,
        )

        cancel_url = reverse("items:cancel", args=[item2.pk])
        response = self.client.post(cancel_url, follow=True)
        self.assertRedirects(response, reverse("items:my_items"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(m.level_tag == "success" for m in messages))

        # Verify the cancel was applied
        item2.refresh_from_db()
        self.assertEqual(item2.status, Item.Status.CANCELADO)

