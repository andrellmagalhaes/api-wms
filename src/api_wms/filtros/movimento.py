"""Filtros utilizados na consulta e exportação de relatórios de movimentos."""

from dataclasses import dataclass
from datetime import date


@dataclass
class FiltrosMovimento:
    """Filtros utilizados na listagem e exportação de relatórios de movimentos.

    :param tipo: Tipo do movimento a ser utilizado como filtro.
    :type tipo: str | None
    :param data_min: Data inicial do período utilizado como filtro.
    :type data_min: date | None
    :param data_max: Data final do período utilizado como filtro.
    :type data_max: date | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    """

    tipo: str | None = None
    data_min: date | None = None
    data_max: date | None = None
    fornecedor_id: int | None = None
