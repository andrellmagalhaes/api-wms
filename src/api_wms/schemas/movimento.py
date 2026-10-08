"""Schemas Pydantic utilizados na validação, serialização e detalhamento de movimentos de entrada e saída de produtos."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api_wms.schemas.item import ItemCreate, ItemResponse


class MovimentoCreate(BaseModel):
    """Schema utilizado para criação de um movimento de entrada ou saída de produtos.

    :param nf_numero: Número da nota fiscal do movimento.
    :type nf_numero: str
    :param nf_chave: Chave de acesso da nota fiscal do movimento.
    :type nf_chave: str
    :param tipo: Tipo de movimento.
    :type tipo: Literal["Entrada", "Saida"]
    :param fornecedor_cnpj: CNPJ do fornecedor de origem ou destino do movimento.
    :type fornecedor_cnpj: str
    :param itens: Lista de itens contidos no movimento.
    :type itens: Sequence[ItemCreate]
    """

    nf_numero: str = Field(
        min_length=1,
        max_length=9,
        pattern=r"^\d{1,9}$",
        description="Número da nota fiscal do movimento",
        examples=["123456789", "999.999.999"],
    )
    nf_chave: str = Field(
        min_length=44,
        max_length=44,
        pattern=r"^\d{44}$",
        description="Chave de acesso da nota fiscal do movimento",
        examples=["35231012345678000195550010000001231234567895"],
    )
    tipo: Literal["Entrada", "Saida"] = Field(description="Tipo de movimento")
    fornecedor_cnpj: str = Field(
        min_length=14,
        max_length=14,
        pattern=r"^[A-Z0-9]{14}$",
        description="CNPJ do fornecedor de origem ou destino do movimento",
        examples=["12345678000195", "12.ABC.345/0001-95"],
    )
    itens: Sequence[ItemCreate] = Field(
        min_length=1, description="Lista de itens contidos no movimento"
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

    @field_validator("nf_numero", mode="before")
    @classmethod
    def processar_nf_numero(cls, valor: Any) -> str:
        """Processa e valida o número da nota fiscal do movimento.

        :param valor: Número da nota fiscal do movimento a ser processado.
        :type valor: Any
        :return: Número da nota fiscal do movimento processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir entre 1 e 9 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "O número da nota fiscal do movimento deve ser enviado como texto."
            )

        valor = valor.replace(".", "")

        if not re.fullmatch(pattern=r"\d{1,9}", string=valor):
            raise ValueError(
                "Número da nota fiscal do movimento inválido. Deve ter entre 1 e 9 caracteres numéricos."
            )

        return valor

    @field_validator("nf_chave", mode="before")
    @classmethod
    def processar_nf_chave(cls, valor: Any) -> str:
        """Processa e valida a chave de acesso da nota fiscal do movimento.

        :param valor: Chave de acesso da nota fiscal do movimento a ser processada.
        :type valor: Any
        :return: Chave de acesso da nota fiscal do movimento processada.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 44 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "A chave de acesso da nota fiscal do movimento deve ser enviada como texto."
            )

        valor = valor.replace(".", "").replace(" ", "")

        if not re.fullmatch(pattern=r"\d{44}", string=valor):
            raise ValueError(
                "Chave de acesso da nota fiscal do movimento inválida. Deve ter exatamente 44 caracteres numéricos."
            )

        return valor

    @field_validator("fornecedor_cnpj", mode="before")
    @classmethod
    def processar_fornecedor_cnpj(cls, valor: Any) -> str:
        """Processa e valida o CNPJ do fornecedor de origem ou destino do movimento.

        :param valor: CNPJ do fornecedor de origem ou destino do movimento a ser processado.
        :type valor: Any
        :return: CNPJ do fornecedor processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 14 caracteres alfanuméricos.
        """
        if not isinstance(valor, str):
            raise ValueError("O CNPJ do fornecedor deve ser enviado como texto.")

        valor = valor.replace(".", "").replace("/", "").replace("-", "").upper()

        if not re.fullmatch(pattern=r"[A-Z0-9]{14}", string=valor):
            raise ValueError(
                "CNPJ do fornecedor inválido. Deve ter exatamente 14 caracteres, restrito a letras e números."
            )

        return valor


class MovimentoResumoResponse(BaseModel):
    """Schema utilizado para resposta resumida com os dados de um movimento.

    :param id: ID do movimento.
    :type id: int
    :param nf_numero: Número da nota fiscal do movimento.
    :type nf_numero: str
    :param nf_chave: Chave de acesso da nota fiscal do movimento.
    :type nf_chave: str
    :param tipo: Tipo de movimento.
    :type tipo: str
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param fornecedor_id: ID do fornecedor de origem ou destino do movimento.
    :type fornecedor_id: int
    :param qtd_itens: Quantidade de itens movimentados.
    :type qtd_itens: int
    :param qtd_unidades: Quantidade de unidades de itens movimentadas.
    :type qtd_unidades: Decimal
    :param valor_total: Valor total do movimento.
    :type valor_total: Decimal
    """

    id: int = Field(description="ID do movimento")
    nf_numero: str = Field(description="Número da nota fiscal do movimento")
    nf_chave: str = Field(description="Chave de acesso da nota fiscal do movimento")
    tipo: str = Field(description="Tipo de movimento")
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    fornecedor_id: int = Field(
        description="ID do fornecedor de origem ou destino do movimento"
    )
    qtd_itens: int = Field(description="Quantidade de itens movimentados")
    qtd_unidades: Decimal = Field(
        description="Quantidade de unidades de itens movimentadas"
    )
    valor_total: Decimal = Field(description="Valor total do movimento")

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class MovimentoDetalhesResponse(MovimentoResumoResponse):
    """Schema utilizado para resposta detalhada com os dados de um movimento.

    :param itens: Lista de itens contidos no movimento.
    :type itens: list[ItemResponse]
    """

    itens: list[ItemResponse] = Field(
        description="Lista de itens contidos no movimento"
    )
