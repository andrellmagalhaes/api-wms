"""Modelo SQLAlchemy utilizado para representar endereços de armazenagem."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_wms.models.base import Base

if TYPE_CHECKING:
    from api_wms.models.produto import Produto


class Endereco(Base):
    """Modelo utilizado para representar um endereço de armazenagem.

    :param id: ID do endereço de armazenagem.
    :type id: int
    :param cea: Código do endereço de armazenagem.
    :type cea: str
    :param status: Status do endereço de armazenagem.
    :type status: bool
    :param produto: Produto armazenado no endereço.
    :type produto: Produto | None
    """

    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="ID do endereco de armazenagem"
    )
    cea: Mapped[str] = mapped_column(
        type_=String(10),
        unique=True,
        nullable=False,
        comment="Código do endereço de armazenagem",
    )
    status: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Status do endereço de armazenagem",
    )

    produto: Mapped[Produto | None] = relationship(back_populates="endereco")
