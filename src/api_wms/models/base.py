"""Classe base utilizada pelos modelos SQLAlchemy da aplicação."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe base para os modelos utilizados pelo SQLAlchemy.

    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora da última atualização do registro.
    :type atualizado_em: datetime
    """

    criado_em: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora de atualização do registro",
    )
