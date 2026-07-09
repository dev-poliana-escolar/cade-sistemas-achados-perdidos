from datetime import date
from pydantic import BaseModel


class ItemContractSchema(BaseModel):
    id: int
    categoria: str
    descricao: str
    cor: str
    local_encontrado: str
    status: str
    dados_sensiveis: bool
    cadastrado_por_id: int
    data_encontro: date