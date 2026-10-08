"""Modelo SQLAlchemy utilizado para representar categorias de produtos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.subcategoria import Subcategoria


class Categoria(Base):
    """Modelo utilizado para representar uma categoria de produtos.

    :param id: ID da categoria.
    :type id: int
    :param nome: Nome da categoria.
    :type nome: str
    :param status: Status da categoria.
    :type status: bool
    :param subcategorias: Subcategorias vinculadas à categoria.
    :type subcategorias: list[Subcategoria]
    """

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID da categoria"
    )
    nome: Mapped[str] = mapped_column(
        type_=String(50), unique=True, nullable=False, comment="Nome da categoria"
    )
    status: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Status da categoria"
    )

    subcategorias: Mapped[list[Subcategoria]] = relationship(back_populates="categoria")
