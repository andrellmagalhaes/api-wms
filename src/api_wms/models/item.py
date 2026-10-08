"""Modelo SQLAlchemy utilizado para representar itens de movimentos de entrada e saída de produtos."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.movimento import Movimento
    from api_wms.models.produto import Produto


class Item(Base):
    """Modelo utilizado para representar um item de um movimento de entrada ou saída de produto.

    :param id: ID do item.
    :type id: int
    :param movimento_id: ID do movimento ao qual o item pertence.
    :type movimento_id: int
    :param produto_id: ID do produto referente ao item.
    :type produto_id: int
    :param qtd_unidades: Quantidade de unidades do produto movimentadas.
    :type qtd_unidades: Decimal
    :param preco_unit: Preço unitário do produto no movimento.
    :type preco_unit: Decimal
    :param movimento: Movimento ao qual o item pertence.
    :type movimento: Movimento
    :param produto: Produto referente ao item.
    :type produto: Produto
    """

    __tablename__ = "itens"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID do item"
    )
    movimento_id: Mapped[int] = mapped_column(
        ForeignKey("movimentos.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID da movimentação do item",
    )
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID do produto referente ao item",
    )
    qtd_unidades: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=3),
        nullable=False,
        comment="Quantidade de unidades do item",
    )
    preco_unit: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Preço unitário do item",
    )

    movimento: Mapped["Movimento"] = relationship(back_populates="itens")
    produto: Mapped["Produto"] = relationship(back_populates="itens")

    __table_args__ = (
        CheckConstraint("qtd_unidades > 0", name="check_qtd_unidades"),
        CheckConstraint("preco_unit >= 0", name="check_preco_unit"),
    )
