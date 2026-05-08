"""
Serviço de cadastro de itens encontrados.
Implementa IItemCadastroService com injeção de repositório.
"""

from typing import Any, Dict

from django.contrib.auth.models import User

from .cadastrar_item_interface import IItemCadastroService
from .cadastrar_item_repository import ItemRepository
from ..models import Item


class CadastrarItemService(IItemCadastroService):
    """
    Serviço de cadastro de itens encontrados.

    Recebe um ItemRepository por injeção de dependência e delega a persistência
    para a camada de repositório.
    """

    CAMPOS_SENSIVEIS = [
        "rg",
        "cpf",
        "cnpj",
        "matrícula",
        "matricula",
        "senha",
        "cartão",
        "cartao",
        "número",
        "numero",
        "documento",
        "identidade",
        "telefone",
        "celular",
        "email",
        "endereço",
        "endereco",
    ]

    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def validar_obrigatoriedade(self, dados: Dict[str, Any]) -> tuple[bool, str]:
        if not dados.get("descricao") or not str(dados.get("descricao")).strip():
            return False, "Descrição do item é obrigatória."

        if not dados.get("local") or not str(dados.get("local")).strip():
            return False, "Local de encontro é obrigatório."

        if not dados.get("imagem"):
            return False, "Imagem é obrigatória."

        if dados.get("usuario_id") is None:
            return False, "Usuário inválido."

        if not dados.get("nome_arquivo_imagem"):
            return False, "Nome do arquivo de imagem é obrigatório."

        if len(str(dados.get("descricao"))) > 500:
            return False, "Descrição não pode exceder 500 caracteres."

        if len(str(dados.get("local"))) > 255:
            return False, "Local não pode exceder 255 caracteres."

        return True, ""

    def cadastrar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        valido, mensagem = self.validar_obrigatoriedade(dados)
        if not valido:
            return {"sucesso": False, "mensagem": mensagem}

        try:
            usuario = User.objects.get(id=int(dados["usuario_id"]))
        except (User.DoesNotExist, KeyError, ValueError):
            return {"sucesso": False, "mensagem": "Usuário não encontrado no sistema."}

        dados_sensiveis = self._detectar_dados_sensiveis(str(dados["descricao"]))

        item = Item(
            descricao=str(dados["descricao"]).strip(),
            imagem=dados["imagem"],
            cor=str(dados.get("cor", "")).strip() or str(dados["local"]).strip(),
            local_encontrado=str(dados["local"]).strip(),
            dados_sensiveis=dados_sensiveis,
            cadastrado_por=usuario,
            status=Item.StatusChoices.PENDENTE,
        )

        try:
            item_salvo = self.repository.salvar(item)
        except Exception as exc:
            return {"sucesso": False, "mensagem": f"Erro ao salvar item: {exc}"}

        return {
            "sucesso": True,
            "item_id": item_salvo.id,
            "mensagem": "Item registrado com sucesso com status PENDENTE.",
        }

    def enviar_instrucoes_entrega(self, item_id: int) -> Dict[str, Any]:
        return {
            "sucesso": True,
            "mensagem": (
                "Item registrado! Dirija-se à COAPAC para entregar o objeto "
                "e validar o cadastro."
            ),
            "item_id": item_id,
        }

    def cancelar_cadastro(self, item_id: int) -> Dict[str, Any]:
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return {"sucesso": False, "mensagem": "Item não encontrado."}

        item.status = Item.StatusChoices.CANCELADO
        try:
            self.repository.salvar(item)
        except Exception as exc:
            return {"sucesso": False, "mensagem": f"Não foi possível cancelar o cadastro: {exc}"}

        return {"sucesso": True, "mensagem": "Cadastro cancelado com sucesso."}

    def _detectar_dados_sensiveis(self, texto: str) -> bool:
        texto_lower = texto.lower()
        return any(campo.lower() in texto_lower for campo in self.CAMPOS_SENSIVEIS)
