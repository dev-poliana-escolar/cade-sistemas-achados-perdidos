from django.test import TestCase

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

from apps.items.forms import ItemForm
from apps.items.models import Item

User = get_user_model()


class CadastroItemTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="pass1234"
        )

        # Minimal valid data for forms and views
        self.base_data = {
            "categoria": Item.Categoria.ELETRONICO,
            "cor": "PRETO",
            "descricao": "Caneta encontrada",
            "local_encontrado": "Bloco A",
            "data_encontro": "2020-01-01T10:00",
        }

        # small in-memory file to simulate an uploaded image
        self.image_file = SimpleUploadedFile(
            name="test.jpg",
            content=b"\x47\x49\x46\x38\x39\x61",
            content_type="image/jpeg",
        )

    def test_form_rejects_blank_required_fields(self):
        data = self.base_data.copy()
        data.update({
            "descricao": "",  # empty
            "local_encontrado": "",  # empty
        })

        form = ItemForm(data=data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn("descricao", form.errors)
        self.assertIn("local_encontrado", form.errors)
        self.assertIn("imagem", form.errors)

    def test_outro_cor_transformed_to_uppercase(self):
        data = self.base_data.copy()
        data.update({
            "cor": "OUTRA",
            "outra_cor": "Azul Turquesa",
        })

        form = ItemForm(data=data, files={"imagem": self.image_file})
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["cor"], "AZUL TURQUESA")

    def test_sensitive_detection_forces_dados_sensiveis(self):
        data = self.base_data.copy()
        # include the keyword 'CPF' and explicitly send dados_sensiveis False
        data.update({
            "descricao": "Documento com CPF: 000.000.000-00",
            "dados_sensiveis": False,
        })

        form = ItemForm(data=data, files={"imagem": self.image_file})
        self.assertTrue(form.is_valid(), msg=form.errors)
        # the form's cleaning should set dados_sensiveis to True
        self.assertTrue(form.cleaned_data.get("dados_sensiveis", False))

    def test_item_create_view_forces_status_pendente(self):
        self.client.login(username="tester", password="pass1234")

        data = self.base_data.copy()
        data["descricao"] = "Relógio encontrado"

        response = self.client.post(
            reverse("items:create"),
            data={**data},
            files={"imagem": self.image_file},
        )

        # After creation, the user is redirected
        self.assertEqual(response.status_code, 302)

        # The item must exist and have status PENDENTE and be associated with the user
        item = Item.objects.get(descricao="Relógio encontrado", cadastrado_por=self.user)
        self.assertEqual(item.status, Item.Status.PENDENTE)

    def test_edit_and_cancel_blocked_when_status_is_valido(self):
        # create an item owned by user but with status VALIDO
        item = Item.objects.create(
            categoria=Item.Categoria.ELETRONICO,
            cor="PRETO",
            descricao="Fone de ouvido",
            local_encontrado="Sala 1",
            data_encontro=timezone.now(),
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
            "data_encontro": item.data_encontro.strftime("%Y-%m-%dT%H:%M"),
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

