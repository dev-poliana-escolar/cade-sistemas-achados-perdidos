from datetime import date

import pytest
from django.urls import reverse

from apps.items.models import Item
from tests_suite.api.schemas.item_schemas import (
    ItemContractSchema
)


@pytest.mark.django_db
class TestItemAPI:

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