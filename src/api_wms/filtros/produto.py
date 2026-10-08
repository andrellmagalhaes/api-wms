"""Filtros utilizados na consulta e exportação de relatórios de produtos."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FiltrosProduto:
    """Filtros utilizados na listagem e exportação de relatórios de produtos.

    :param nome: Nome do produto a ser utilizado como filtro.
    :type nome: str | None
    :param sku: SKU do produto a ser utilizado como filtro.
    :type sku: str | None
    :param ncm: NCM do produto a ser utilizado como filtro.
    :type ncm: str | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    :param subcategoria_id: ID da subcategoria utilizada como filtro.
    :type subcategoria_id: int | None
    :param estoque_atual_min: Quantidade mínima de estoque atual utilizada como filtro.
    :type estoque_atual_min: Decimal | None
    :param estoque_atual_max: Quantidade máxima de estoque atual utilizada como filtro.
    :type estoque_atual_max: Decimal | None
    :param unidade_id: ID da unidade utilizada como filtro.
    :type unidade_id: int | None
    :param status: Status do produto a ser utilizado como filtro.
    :type status: bool | None
    """

    nome: str | None = None
    sku: str | None = None
    ncm: str | None = None
    fornecedor_id: int | None = None
    subcategoria_id: int | None = None
    estoque_atual_min: Decimal | None = None
    estoque_atual_max: Decimal | None = None
    unidade_id: int | None = None
    status: bool | None = None
