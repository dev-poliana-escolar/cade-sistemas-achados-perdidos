import unittest
from unittest.mock import Mock, patch

from apps.items.registerItem.register_item_services import CadastrarItemService
from apps.items.registerItem.cadastrar_item_repository import ItemRepository


class FakeItem:
    class StatusChoices:
        PENDENTE = "PENDENTE"

    def __init__(
        self,
        descricao,
        imagem,
        cor,
        local_encontrado,
        dados_sensiveis,
        cadastrado_por,
        status,
    ):
        self.descricao = descricao
        self.imagem = imagem
        self.cor = cor
        self.local_encontrado = local_encontrado
        self.dados_sensiveis = dados_sensiveis
        self.cadastrado_por = cadastrado_por
        self.status = status

    def full_clean(self):
        return None

    def save(self):
        return None


class DummyUser:
    pass


class TestCadastrarItemService(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_data = {
            "descricao": "Chaveiro preto encontrado no Bloco A",
            "imagem": b"fake-image-bytes",
            "cor": "Preto",
            "local": "Bloco A",
            "nome_arquivo_imagem": "chaveiro.jpg",
            "usuario_id": 1,
            "status": "VALIDO",
        }
        self.dummy_user = DummyUser()

    def _service_with_repo(self, repository):
        return CadastrarItemService(repository)

    @patch("apps.items.registerItem.register_item_services.Item", new=FakeItem)
    @patch("apps.items.registerItem.register_item_services.User.objects.get")
    def test_service_fails_without_repository_contract(self, mock_get):
        mock_get.return_value = self.dummy_user
        bad_repo = object()
        service = self._service_with_repo(bad_repo)

        with self.assertRaises(AttributeError):
            service.cadastrar(self.valid_data)

    @patch("apps.items.registerItem.register_item_services.Item", new=FakeItem)
    @patch("apps.items.registerItem.register_item_services.User.objects.get")
    def test_cadastrar_overwrites_status_to_pendente(self, mock_get):
        mock_get.return_value = self.dummy_user
        repository = Mock(spec=ItemRepository)
        repository.salvar = Mock(side_effect=lambda item: item)

        service = self._service_with_repo(repository)
        result = service.cadastrar(self.valid_data)

        self.assertTrue(result.get("sucesso"))
        repository.salvar.assert_called_once()

        saved_item = repository.salvar.call_args[0][0]
        self.assertEqual(saved_item.status, FakeItem.StatusChoices.PENDENTE)

    @patch("apps.items.registerItem.register_item_services.Item", new=FakeItem)
    @patch("apps.items.registerItem.register_item_services.User.objects.get")
    def test_cadastrar_returns_failure_for_missing_required_fields(self, mock_get):
        mock_get.return_value = self.dummy_user
        repository = Mock(spec=ItemRepository)
        repository.salvar = Mock(side_effect=lambda item: item)

        service = self._service_with_repo(repository)
        invalid_data = self.valid_data.copy()
        invalid_data.pop("imagem")

        result = service.cadastrar(invalid_data)

        self.assertFalse(result.get("sucesso"))
        self.assertIn("Imagem é obrigatória", result.get("mensagem", ""))
        repository.salvar.assert_not_called()

    @patch("apps.items.registerItem.register_item_services.Item", new=FakeItem)
    @patch("apps.items.registerItem.register_item_services.User.objects.get")
    def test_repository_persist_called_once_with_correct_item(self, mock_get):
        mock_get.return_value = self.dummy_user
        repository = Mock(spec=ItemRepository)
        repository.salvar = Mock(side_effect=lambda item: item)

        service = self._service_with_repo(repository)
        result = service.cadastrar(self.valid_data)

        self.assertTrue(result.get("sucesso"))
        repository.salvar.assert_called_once()

        saved_item = repository.salvar.call_args[0][0]
        self.assertEqual(saved_item.descricao, self.valid_data["descricao"])
        self.assertEqual(saved_item.imagem, self.valid_data["imagem"])
        self.assertEqual(saved_item.local_encontrado, self.valid_data["local"])
        self.assertEqual(saved_item.cor, self.valid_data["cor"])
        self.assertEqual(saved_item.cadastrado_por, self.dummy_user)

    @patch("apps.items.registerItem.register_item_services.Item", new=FakeItem)
    @patch("apps.items.registerItem.register_item_services.User.objects.get")
    def test_cadastrar_marks_sensitive_data_when_description_contains_cpf(self, mock_get):
        mock_get.return_value = self.dummy_user
        repository = Mock(spec=ItemRepository)
        repository.salvar = Mock(side_effect=lambda item: item)

        service = self._service_with_repo(repository)
        sensitive_data = self.valid_data.copy()
        sensitive_data["descricao"] = "Carteira com RG e CPF encontrados no Bloco A"

        result = service.cadastrar(sensitive_data)

        self.assertTrue(result.get("sucesso"))
        saved_item = repository.salvar.call_args[0][0]
        self.assertTrue(saved_item.dados_sensiveis)


if __name__ == "__main__":
    unittest.main()
