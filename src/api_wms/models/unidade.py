"""Modelo SQLAlchemy utilizado para representar unidades de medida de produtos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.produto import Produto


class Unidade(Base):
    """Modelo utilizado para representar uma unidade de medida de produtos.

    :param id: ID da unidade de medida.
    :type id: int
    :param nome: Nome da unidade de medida.
    :type nome: str
    :param sigla: Sigla da unidade de medida.
    :type sigla: str
    :param status: Status da unidade de medida.
    :type status: bool
    :param produtos: Produtos que utilizam a unidade de medida.
    :type produtos: list[Produto]
    """

    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID da unidade de medida"
    )
    nome: Mapped[str] = mapped_column(
        type_=String(50),
        unique=True,
        nullable=False,
        comment="Nome da unidade de medida",
    )
    sigla: Mapped[str] = mapped_column(
        type_=String(10),
        unique=True,
        nullable=False,
        comment="Sigla da unidade de medida",
    )
    status: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Status da unidade de medida"
    )

    produtos: Mapped[list["Produto"]] = relationship(back_populates="unidade")
