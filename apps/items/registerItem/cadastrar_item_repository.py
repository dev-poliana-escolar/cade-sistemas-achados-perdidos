"""
Repositório de persistência para itens encontrados.
"""

from ..models import Item


class ItemRepository:
    """
    Repositório responsável por persistir a entidade Item.
    """

    def salvar(self, item: Item) -> Item:
        """Salva o item no banco de dados."""
        item.full_clean()
        item.save()
        return item
