"""
Interfaces para o registro de itens encontrados.
Implementa o Princípio da Inversão de Dependência (DIP).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ItemCadastroResultado:
    """Resultado padronizado do cadastro de item."""
    sucesso: bool
    item_id: Optional[int] = None
    mensagem: str = ""


class IItemCadastroService(ABC):
    """
    Interface abstrata para serviço de cadastro de itens encontrados.
    """

    @abstractmethod
    def validar_obrigatoriedade(self, dados: Dict[str, Any]) -> tuple[bool, str]:
        """Valida se os campos obrigatórios do cadastro estão presentes."""
        pass

    @abstractmethod
    def cadastrar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra um item encontrado e retorna o resultado da operação."""
        pass

    @abstractmethod
    def enviar_instrucoes_entrega(self, item_id: int) -> Dict[str, Any]:
        """Gera instruções de entrega após cadastro bem-sucedido."""
        pass

    @abstractmethod
    def cancelar_cadastro(self, item_id: int) -> Dict[str, Any]:
        """Cancela o cadastro de um item pendente."""
        pass
