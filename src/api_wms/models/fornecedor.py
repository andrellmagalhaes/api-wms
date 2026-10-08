"""Modelo SQLAlchemy utilizado para representar fornecedores de produtos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.movimento import Movimento
    from api_wms.models.produto import Produto


class Fornecedor(Base):
    """Modelo utilizado para representar um fornecedor de produtos.

    :param id: ID do fornecedor.
    :type id: int
    :param nome: Nome do fornecedor.
    :type nome: str
    :param cnpj: CNPJ do fornecedor.
    :type cnpj: str
    :param email: Endereço de email do fornecedor.
    :type email: str | None
    :param telefone: Número de telefone do fornecedor.
    :type telefone: str | None
    :param status: Status do fornecedor.
    :type status: bool
    :param produtos: Produtos fornecidos pelo fornecedor.
    :type produtos: list[Produto]
    :param movimentos: Movimentos vinculados ao fornecedor.
    :type movimentos: list[Movimento]
    """

    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID do fornecedor"
    )
    nome: Mapped[str] = mapped_column(
        type_=String(50), unique=True, nullable=False, comment="Nome do fornecedor"
    )
    cnpj: Mapped[str] = mapped_column(
        type_=String(14), unique=True, nullable=False, comment="CNPJ do fornecedor"
    )
    email: Mapped[str | None] = mapped_column(
        type_=String(50), comment="Endereço de email do fornecedor"
    )
    telefone: Mapped[str | None] = mapped_column(
        type_=String(11), comment="Número de telefone do fornecedor"
    )
    status: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Status do fornecedor"
    )

    produtos: Mapped[list["Produto"]] = relationship(back_populates="fornecedor")
    movimentos: Mapped[list["Movimento"]] = relationship(back_populates="fornecedor")
