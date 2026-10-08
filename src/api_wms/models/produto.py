"""Modelo SQLAlchemy utilizado para representar produtos armazenados no estoque."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.endereco import Endereco
    from api_wms.models.fornecedor import Fornecedor
    from api_wms.models.movimento import Item
    from api_wms.models.subcategoria import Subcategoria
    from api_wms.models.unidade import Unidade


class Produto(Base):
    """Modelo utilizado para representar um produto armazenado no estoque.

    :param id: ID do produto.
    :type id: int
    :param nome: Nome do produto.
    :type nome: str
    :param descricao: Descrição do produto.
    :type descricao: str
    :param sku: Código SKU do produto.
    :type sku: str
    :param barcode: Código de barras EAN-13 do produto.
    :type barcode: str
    :param ncm: Código NCM do produto.
    :type ncm: str
    :param endereco_id: ID do endereço de armazenagem do produto.
    :type endereco_id: int
    :param fornecedor_id: ID do fornecedor do produto.
    :type fornecedor_id: int
    :param subcategoria_id: ID da subcategoria do produto.
    :type subcategoria_id: int
    :param estoque_atual: Quantidade atual de estoque do produto.
    :type estoque_atual: Decimal
    :param estoque_min: Quantidade mínima de estoque do produto.
    :type estoque_min: Decimal
    :param estoque_max: Quantidade máxima de estoque do produto.
    :type estoque_max: Decimal
    :param unidade_id: ID da unidade de medida do produto.
    :type unidade_id: int
    :param preco_venda: Preço de venda do produto.
    :type preco_venda: Decimal
    :param preco_custo: Preço de custo do produto.
    :type preco_custo: Decimal
    :param status: Status do produto.
    :type status: bool
    :param endereco: Endereço de armazenagem do produto.
    :type endereco: Endereco
    :param fornecedor: Fornecedor do produto.
    :type fornecedor: Fornecedor
    :param itens: Itens de movimentos vinculados ao produto.
    :type itens: list[Item]
    :param subcategoria: Subcategoria à qual o produto pertence.
    :type subcategoria: Subcategoria
    :param unidade: Unidade de medida do produto.
    :type unidade: Unidade
    """

    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID do produto"
    )
    nome: Mapped[str] = mapped_column(
        type_=String(50), unique=True, nullable=False, comment="Nome do produto"
    )
    descricao: Mapped[str] = mapped_column(
        type_=String(75), nullable=False, comment="Descrição do produto"
    )
    sku: Mapped[str] = mapped_column(
        type_=String(25), unique=True, nullable=False, comment="Código SKU do produto"
    )
    barcode: Mapped[str] = mapped_column(
        type_=String(13),
        unique=True,
        nullable=False,
        comment="Código de barras EAN-13 do produto",
    )
    ncm: Mapped[str] = mapped_column(
        type_=String(8),
        nullable=False,
        comment="Código NCM do produto",
    )
    endereco_id: Mapped[int] = mapped_column(
        ForeignKey("enderecos.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        comment="ID do endereço de armazenagem do produto",
    )
    fornecedor_id: Mapped[int] = mapped_column(
        ForeignKey("fornecedores.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID do fornecedor do produto",
    )
    subcategoria_id: Mapped[int] = mapped_column(
        ForeignKey("subcategorias.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID da subcategoria do produto",
    )
    estoque_atual: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=3),
        default=Decimal("0.000"),
        nullable=False,
        comment="Estoque atual do produto",
    )
    estoque_min: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=3),
        default=Decimal("0.000"),
        nullable=False,
        comment="Estoque mínimo do produto",
    )
    estoque_max: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=3),
        default=Decimal("0.000"),
        nullable=False,
        comment="Estoque máximo do produto",
    )
    unidade_id: Mapped[int] = mapped_column(
        ForeignKey("unidades.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID da unidade de medida do produto",
    )
    preco_venda: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Preço de venda do produto",
    )
    preco_custo: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Preço de custo do produto",
    )
    status: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Status do produto"
    )

    endereco: Mapped[Endereco] = relationship(back_populates="produto")
    fornecedor: Mapped[Fornecedor] = relationship(back_populates="produtos")
    itens: Mapped[list["Item"]] = relationship(back_populates="produto")
    subcategoria: Mapped[Subcategoria] = relationship(back_populates="produtos")
    unidade: Mapped[Unidade] = relationship(back_populates="produtos")

    __table_args__ = (
        CheckConstraint(sqltext="estoque_atual >= 0", name="check_estoque_atual"),
        CheckConstraint(sqltext="estoque_min >= 0", name="check_estoque_min"),
        CheckConstraint(sqltext="estoque_max >= 0", name="check_estoque_max"),
        CheckConstraint(sqltext="preco_venda >= 0", name="check_preco_venda"),
        CheckConstraint(sqltext="preco_custo >= 0", name="check_preco_custo"),
    )
