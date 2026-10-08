"""Modelo SQLAlchemy utilizado para representar movimentos de entrada e saída de produtos."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.fornecedor import Fornecedor
    from api_wms.models.item import Item


class Movimento(Base):
    """Modelo utilizado para representar um movimento de entrada ou saída de produtos.

    :param id: ID do movimento.
    :type id: int
    :param nf_numero: Número da nota fiscal do movimento.
    :type nf_numero: str
    :param nf_chave: Chave de acesso da nota fiscal do movimento.
    :type nf_chave: str
    :param tipo: Tipo do movimento, podendo ser entrada ou saída.
    :type tipo: str
    :param fornecedor_id: ID do fornecedor de origem ou destino do movimento.
    :type fornecedor_id: int
    :param itens: Itens pertencentes ao movimento.
    :type itens: list[Item]
    :param fornecedor: Fornecedor de origem ou destino do movimento.
    :type fornecedor: Fornecedor
    """

    __tablename__ = "movimentos"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID do movimento"
    )
    nf_numero: Mapped[str] = mapped_column(
        type_=String(9),
        nullable=False,
        comment="Número da nota fiscal do movimento",
    )
    nf_chave: Mapped[str] = mapped_column(
        type_=String(44),
        unique=True,
        nullable=False,
        comment="Chave de acesso da nota fiscal do movimento",
    )
    tipo: Mapped[str] = mapped_column(
        type_=String(7),
        nullable=False,
        comment="Tipo de movimento",
    )
    fornecedor_id: Mapped[int] = mapped_column(
        ForeignKey("fornecedores.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID do fornecedor de origem ou destino do movimento",
    )

    itens: Mapped[list["Item"]] = relationship(back_populates="movimento")
    fornecedor: Mapped["Fornecedor"] = relationship(back_populates="movimentos")

    __table_args__ = (
        CheckConstraint("tipo IN ('Entrada', 'Saida')", name="check_tipo"),
    )

    @property
    def qtd_itens(self) -> int:
        return len(self.itens) if self.itens else 0

    @property
    def qtd_unidades(self) -> Decimal:
        return sum((item.qtd_unidades for item in self.itens), Decimal("0.00"))

    @property
    def valor_total(self) -> Decimal:
        return sum(
            (item.qtd_unidades * item.preco_unit for item in self.itens),
            Decimal("0.00"),
        )
