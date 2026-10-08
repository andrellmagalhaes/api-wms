"""Schemas Pydantic utilizados na validação e serialização de itens de movimentos."""

import re
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api_wms.schemas.produto import ProdutoResponse


class ItemCreate(BaseModel):
    """Schema utilizado para criação de um item de movimento.

    :param barcode: Código de barras EAN-13 do item.
    :type barcode: str
    :param qtd_unidades: Quantidade de unidades do item.
    :type qtd_unidades: Decimal
    :param preco_unit: Preço unitário do item na movimentação.
    :type preco_unit: Decimal
    """

    barcode: str = Field(
        min_length=13,
        max_length=13,
        pattern=r"^\d{13}$",
        description="Código de barras EAN-13 do item",
        examples=["7891020304050", "789-1020-304050"],
    )
    qtd_unidades: Decimal = Field(
        gt=Decimal("0.00"),
        description="Quantidade de unidades do item",
    )
    preco_unit: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Preço unitário do item na movimentação",
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

    @field_validator("barcode", mode="before")
    @classmethod
    def processar_barcode(cls, valor: Any) -> str:
        """Processa e valida o código de barras EAN-13 do item.

        :param valor: Código de barras EAN-13 do item a ser processado.
        :type valor: Any
        :return: Código de barras EAN-13 do item processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 13 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "O código de barras EAN-13 do item deve ser enviado como texto."
            )

        valor = valor.replace("-", "")

        if not re.fullmatch(pattern=r"\d{13}", string=valor):
            raise ValueError(
                "Código de barras EAN-13 do item inválido. Deve ter exatamente 13 caracteres numéricos."
            )

        return valor


class ItemResponse(BaseModel):
    """Schema utilizado para resposta com os dados de um item de movimento.

    :param id: ID do item.
    :type id: int
    :param produto: Produto referente ao item.
    :type produto: ProdutoResponse
    :param qtd_unidades: Quantidade de unidades do item.
    :type qtd_unidades: Decimal
    :param preco_unit: Preço unitário do item na movimentação.
    :type preco_unit: Decimal
    """

    id: int = Field(description="ID do item")
    produto: ProdutoResponse = Field(description="Produto referente ao item")
    qtd_unidades: Decimal = Field(description="Quantidade de unidades do item")
    preco_unit: Decimal = Field(description="Preço unitário do item na movimentação")

    model_config: ConfigDict = ConfigDict(from_attributes=True)
