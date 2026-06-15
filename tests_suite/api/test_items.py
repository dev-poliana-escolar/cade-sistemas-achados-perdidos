from datetime import date

import pytest
from django.urls import reverse

from apps.items.models import Item
from tests_suite.api.schemas.item_schemas import (
    ItemContractSchema
)


@pytest.mark.django_db
class TestItemAPI:

    # get item tests
    def test_get_item_success(
        self,
        authenticated_client,
        test_user
    ):
        item = Item.objects.create(
            categoria="ELETRONICO",
            descricao="Carregador",
            cor="Preto",
            local_encontrado="Biblioteca",
            data_encontro=date.today(),
            cadastrado_por=test_user,
        )

        response = authenticated_client.get(
            reverse(
                "items:api_item_detail",
                kwargs={"pk": item.pk}
            )
        )

        assert response.status_code == 200

        data = response.json()

        validated = (
            ItemContractSchema.model_validate(data)
        )

        assert validated.id == item.id

    def test_get_item_not_found(
        self,
        authenticated_client
    ):
        response = authenticated_client.get(
            reverse(
                "items:api_item_detail",
                kwargs={"pk": 99999}
            )
        )

        assert response.status_code == 404

    def test_get_item_anonymous(
        self,
        anonymous_client
    ):
        response = anonymous_client.get(
            reverse(
                "items:api_item_detail",
                kwargs={"pk": 1}
            )
        )

        assert response.status_code == 302
    

    # create item tests
    def test_create_item_success(
        self,
        authenticated_client,
    ):
        response = authenticated_client.post(
            reverse("items:api_item_create"),
            {
                "categoria": "ELETRONICO",
                "descricao": "Carregador",
                "cor": "PRETO",
                "local_encontrado": "Biblioteca",
                "dados_sensiveis": False,
                "data_encontro": str(date.today()),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert "id" in data

    def test_create_item_invalid_data(
        self,
        authenticated_client,
    ):
        response = authenticated_client.post(
            reverse("items:api_item_create"),
            {
                "categoria": "",
                "descricao": "",
            },
        )

        assert response.status_code == 400

    def test_create_item_anonymous(
        self,
        anonymous_client,
    ):
        response = anonymous_client.post(
            reverse("items:api_item_create"),
            {}
        )

        assert response.status_code == 302

     # cancel item tests
    def test_cancel_item_success(
        self,
        authenticated_client,
        test_user,
    ):
        item = Item.objects.create(
            categoria="ELETRONICO",
            descricao="Mouse",
            cor="Preto",
            local_encontrado="Lab",
            data_encontro=date.today(),
            status=Item.Status.PENDENTE,
            cadastrado_por=test_user,
        )

        response = authenticated_client.post(
            reverse(
                "items:api_item_cancel",
                kwargs={"pk": item.pk},
            )
        )

        assert response.status_code == 200

        item.refresh_from_db()

        assert (
            item.status
            == Item.Status.CANCELADO
        )

    def test_cancel_item_already_processed(
        self,
        authenticated_client,
        test_user,
    ):
        item = Item.objects.create(
            categoria="ELETRONICO",
            descricao="Mouse",
            cor="Preto",
            local_encontrado="Lab",
            data_encontro=date.today(),
            status=Item.Status.ENTREGUE,
            cadastrado_por=test_user,
        )

        response = authenticated_client.post(
            reverse(
                "items:api_item_cancel",
                kwargs={"pk": item.pk},
            )
        )

        assert response.status_code == 400
    
    def test_cancel_item_anonymous(
        self,
        test_user,
        anonymous_client,
    ):
        item = Item.objects.create(
            categoria="ELETRONICO",
            descricao="Mouse",
            cor="Preto",
            local_encontrado="Lab",
            data_encontro=date.today(),
            cadastrado_por=test_user,
        )

        response = anonymous_client.post(
            reverse(
                "items:api_item_cancel",
                kwargs={"pk": item.pk},
            )
        )

        assert response.status_code == 302