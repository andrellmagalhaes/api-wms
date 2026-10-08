"""Schemas Pydantic utilizados na validação e serialização de unidades de medida."""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UnidadeCreate(BaseModel):
    """Schema utilizado para criação de uma unidade de medida.

    :param nome: Nome da unidade de medida.
    :type nome: str
    :param sigla: Sigla da unidade de medida.
    :type sigla: str
    :param status: Status da unidade de medida.
    :type status: bool
    """

    nome: str = Field(
        min_length=5, max_length=50, description="Nome da unidade de medida"
    )
    sigla: str = Field(
        min_length=1,
        max_length=10,
        pattern=r"^[a-zA-Z0-9]{1,10}$",
        description="Sigla da unidade de medida",
        examples=["UN", "m2"],
    )
    status: bool = Field(default=True, description="Status da unidade de medida")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("sigla", mode="before")
    @classmethod
    def processar_sigla(cls, valor: Any) -> str:
        """Processa e valida a sigla da unidade de medida.

        :param valor: Sigla da unidade de medida a ser processada.
        :type valor: Any
        :return: Sigla da unidade de medida processada.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir entre 1 e 10 caracteres alfanuméricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "A sigla da unidade de medida deve ser enviada como texto."
            )

        valor = valor.upper()

        if not re.fullmatch(pattern=r"[A-Z0-9]{1,10}", string=valor):
            raise ValueError(
                "Sigla da unidade de medida inválida. Deve ter entre 1 e 10 caracteres, restrito a letras e números."
            )

        return valor


class UnidadeResponse(BaseModel):
    """Schema utilizado para resposta com os dados de uma unidade de medida.

    :param id: ID da unidade de medida.
    :type id: int
    :param nome: Nome da unidade de medida.
    :type nome: str
    :param sigla: Sigla da unidade de medida.
    :type sigla: str
    :param status: Status da unidade de medida.
    :type status: bool
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID da unidade de medida")
    nome: str = Field(description="Nome da unidade de medida")
    sigla: str = Field(description="Sigla da unidade de medida")
    status: bool = Field(description="Status da unidade de medida")
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class UnidadeUpdate(BaseModel):
    """Schema utilizado para atualização de uma unidade de medida.

    :param nome: Nome da unidade de medida.
    :type nome: str | None
    :param sigla: Sigla da unidade de medida.
    :type sigla: str | None
    :param status: Status da unidade de medida.
    :type status: bool | None
    """

    nome: str | None = Field(
        min_length=5,
        max_length=50,
        default=None,
        description="Nome da unidade de medida",
    )
    sigla: str | None = Field(
        min_length=1,
        max_length=10,
        default=None,
        pattern=r"^[a-zA-Z0-9]{1,10}$",
        description="Sigla da unidade de medida",
        examples=["UN", "m2"],
    )
    status: bool | None = Field(default=None, description="Status da unidade de medida")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("sigla", mode="before")
    @classmethod
    def processar_sigla(cls, valor: Any) -> str | None:
        """Processa e valida a sigla da unidade de medida.

        :param valor: Sigla da unidade de medida a ser processada.
        :type valor: Any
        :return: Sigla da unidade de medida processada ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir entre 1 e 10 caracteres alfanuméricos.
        """
        if valor is not None:
            if not isinstance(valor, str):
                raise ValueError(
                    "A sigla da unidade de medida deve ser enviada como texto."
                )

            valor = valor.upper()

            if not re.fullmatch(pattern=r"[A-Z0-9]{1,10}", string=valor):
                raise ValueError(
                    "Sigla da unidade de medida inválida. Deve ter entre 1 e 10 caracteres, restrito a letras e números."
                )

        return valor
