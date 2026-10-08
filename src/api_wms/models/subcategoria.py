"""Modelo SQLAlchemy utilizado para representar subcategorias de produtos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.categoria import Categoria
    from api_wms.models.produto import Produto


class Subcategoria(Base):
    """Modelo utilizado para representar uma subcategoria de produtos.

    :param id: ID da subcategoria.
    :type id: int
    :param nome: Nome da subcategoria.
    :type nome: str
    :param categoria_id: ID da categoria à qual a subcategoria pertence.
    :type categoria_id: int
    :param status: Status da subcategoria.
    :type status: bool
    :param categoria: Categoria à qual a subcategoria pertence.
    :type categoria: Categoria
    :param produtos: Produtos pertencentes à subcategoria.
    :type produtos: list[Produto]
    """

    __tablename__ = "subcategorias"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID da subcategoria"
    )
    nome: Mapped[str] = mapped_column(
        type_=String(50), nullable=False, comment="Nome da subcategoria"
    )
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID da categoria referente à subcategoria",
    )
    status: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Status da subcategoria"
    )

    categoria: Mapped[Categoria] = relationship(back_populates="subcategorias")
    produtos: Mapped[list[Produto]] = relationship(back_populates="subcategoria")

    __table_args__ = (
        UniqueConstraint("nome", "categoria_id", name="unique_nome_categoria_id"),
    )
