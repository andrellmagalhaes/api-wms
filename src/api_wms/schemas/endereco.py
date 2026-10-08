"""Schemas Pydantic utilizados na validação e serialização de endereços de armazenagem."""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api_wms.schemas.produto import ProdutoResponse


class EnderecoCreate(BaseModel):
    """Schema utilizado para criação de um endereço de armazenagem.

    :param cea: Código do endereço de armazenagem.
    :type cea: str
    :param status: Status do endereço de armazenagem.
    :type status: bool
    """

    cea: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$",
        description="Código do endereço de armazenagem",
        examples=["0105120301", "01-05-12-03-01"],
    )
    status: bool = Field(default=True, description="Status do endereço de armazenagem")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("cea", mode="before")
    @classmethod
    def processar_cea(cls, valor: Any) -> str:
        """Processa e valida o código do endereço de armazenagem.

        :param valor: Código do endereço de armazenagem a ser processado.
        :type valor: Any
        :return: Código do endereço de armazenagem processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 10 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "O código do endereço de armazenagem deve ser enviado como texto."
            )

        valor = valor.replace("-", "")

        if not re.fullmatch(pattern=r"\d{10}", string=valor):
            raise ValueError(
                "Código do endereço de armazenagem inválido. Deve ter exatamente 10 caracteres numéricos."
            )

        return valor


class EnderecoResponse(BaseModel):
    """Schema utilizado para resposta com os dados de um endereço de armazenagem.

    :param id: ID do endereco de armazenagem.
    :type id: int
    :param cea: Código do endereço de armazenagem.
    :type cea: str
    :param status: Status do endereço de armazenagem.
    :type status: bool
    :param produto: Produto contido no endereço de armazenagem.
    :type produto: ProdutoResponse | None
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID do endereco de armazenagem")
    cea: str = Field(description="Código do endereço de armazenagem")
    status: bool = Field(description="Status do endereço de armazenagem")
    produto: ProdutoResponse | None = Field(
        description="Produto contido no endereço de armazenagem"
    )
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class EnderecoUpdate(BaseModel):
    """Schema utilizado para atualização de um endereço de armazenagem.

    :param cea: Código do endereço de armazenagem.
    :type cea: str | None
    :param status: Status do endereço de armazenagem.
    :type status: bool | None
    """

    cea: str | None = Field(
        min_length=10,
        max_length=10,
        default=None,
        pattern=r"^\d{10}$",
        description="Código do endereço de armazenagem",
        examples=["0105120301", "01-05-12-03-01"],
    )
    status: bool | None = Field(
        default=None, description="Status do endereço de armazenagem"
    )

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("cea", mode="before")
    @classmethod
    def processar_cea(cls, valor: Any) -> str | None:
        """Processa e valida o código do endereço de armazenagem.

        :param valor: Código do endereço de armazenagem a ser processado.
        :type valor: Any
        :return: Código do endereço de armazenagem processado.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 10 caracteres numéricos.
        """
        if valor is not None:
            if not isinstance(valor, str):
                raise ValueError(
                    "O código do endereço de armazenagem deve ser enviado como texto."
                )

            valor = valor.replace("-", "")

            if not re.fullmatch(pattern=r"\d{10}", string=valor):
                raise ValueError(
                    "Código do endereço de armazenagem inválido. Deve ter exatamente 10 caracteres numéricos."
                )

        return valor
