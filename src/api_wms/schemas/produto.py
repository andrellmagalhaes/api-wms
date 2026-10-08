"""Schemas Pydantic utilizados na validação e serialização de produtos."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoCreate(BaseModel):
    """Schema utilizado para criação de um produto.

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
    :type endereco_id: int | None
    :param fornecedor_id: ID do fornecedor do produto.
    :type fornecedor_id: int
    :param subcategoria_id: ID da subcategoria do produto.
    :type subcategoria_id: int
    :param estoque_atual: Estoque atual do produto.
    :type estoque_atual: Decimal
    :param estoque_min: Estoque mínimo do produto.
    :type estoque_min: Decimal
    :param estoque_max: Estoque máximo do produto.
    :type estoque_max: Decimal
    :param unidade_id: ID da unidade de medida do produto.
    :type unidade_id: int
    :param preco_venda: Preço de venda do produto.
    :type preco_venda: Decimal
    :param preco_custo: Preço de custo do produto.
    :type preco_custo: Decimal
    :param status: Status do produto.
    :type status: bool
    """

    nome: str = Field(min_length=5, max_length=50, description="Nome do produto")
    descricao: str = Field(
        min_length=5, max_length=75, description="Descrição do produto"
    )
    sku: str = Field(
        min_length=5,
        max_length=25,
        pattern=r"^[A-Z0-9\-]{5,25}$",
        description="Código SKU do produto",
        examples=["CAMMASCGBR", "CAM-MASC-G-BR"],
    )
    barcode: str = Field(
        min_length=13,
        max_length=13,
        pattern=r"^\d{13}$",
        description="Código de barras EAN-13 do produto",
        examples=["7891020304050", "789-1020-304050"],
    )
    ncm: str = Field(
        min_length=8,
        max_length=8,
        pattern=r"^\d{8}$",
        description="Código NCM do produto",
        examples=["61091000", "2202.10.00"],
    )
    endereco_id: int | None = Field(
        default=None, description="ID do endereço de armazenagem do produto"
    )
    fornecedor_id: int = Field(description="ID do fornecedor do produto")
    subcategoria_id: int = Field(description="ID da subcategoria do produto")
    estoque_atual: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Estoque atual do produto",
    )
    estoque_min: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Estoque mínimo do produto",
    )
    estoque_max: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Estoque máximo do produto",
    )
    unidade_id: int = Field(description="ID da unidade de medida do produto")
    preco_venda: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Preço de venda do produto",
    )
    preco_custo: Decimal = Field(
        ge=Decimal("0.00"),
        default=Decimal("0.00"),
        description="Preço de custo do produto",
    )
    status: bool = Field(default=True, description="Status do produto")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("sku", mode="before")
    @classmethod
    def processar_sku(cls, valor: Any) -> str:
        """Processa e valida o código SKU do produto.

        :param valor: Código SKU do produto a ser processado.
        :type valor: Any
        :return: Código SKU do produto processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir entre 5 e 25 caracteres válidos.
        """
        if not isinstance(valor, str):
            raise ValueError("O código SKU do produto deve ser enviado como texto.")

        valor = valor.upper()

        if not re.fullmatch(pattern=r"[A-Z0-9\-]{5,25}", string=valor):
            raise ValueError(
                "Código SKU do produto inválido. Deve ter entre 5 e 25 caracteres, restrito a letras, números e hifens."
            )

        return valor

    @field_validator("barcode", mode="before")
    @classmethod
    def processar_barcode(cls, valor: Any) -> str:
        """Processa e valida o código de barras EAN-13 do produto.

        :param valor: Código de barras EAN-13 do produto a ser processado.
        :type valor: Any
        :return: Código de barras EAN-13 do produto processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 13 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "O código de barras EAN-13 do produto deve ser enviado como texto."
            )

        valor = valor.replace("-", "")

        if not re.fullmatch(pattern=r"\d{13}", string=valor):
            raise ValueError(
                "Código de barras EAN-13 do produto inválido. Deve ter exatamente 13 caracteres numéricos."
            )

        return valor

    @field_validator("ncm", mode="before")
    @classmethod
    def processar_ncm(cls, valor: Any) -> str:
        """Processa e valida o código NCM do produto.

        :param valor: Código NCM do produto a ser processado.
        :type valor: Any
        :return: Código NCM do produto processado.
        :rtype: str
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 8 caracteres numéricos.
        """
        if not isinstance(valor, str):
            raise ValueError("O código NCM do produto deve ser enviado como texto.")

        valor = valor.replace(".", "")

        if not re.fullmatch(pattern=r"\d{8}", string=valor):
            raise ValueError(
                "Código NCM do produto inválido. Deve ter exatamente 8 caracteres numéricos."
            )

        return valor


class ProdutoResponse(BaseModel):
    """Schema utilizado para resposta com os dados de um produto.

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
    :param estoque_atual: Estoque atual do produto.
    :type estoque_atual: Decimal
    :param estoque_min: Estoque mínimo do produto.
    :type estoque_min: Decimal
    :param estoque_max: Estoque máximo do produto.
    :type estoque_max: Decimal
    :param unidade_id: ID da unidade de medida do produto.
    :type unidade_id: int
    :param preco_venda: Preço de venda do produto.
    :type preco_venda: Decimal
    :param preco_custo: Preço de custo do produto.
    :type preco_custo: Decimal
    :param status: Status do produto.
    :type status: bool
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID do produto")
    nome: str = Field(description="Nome do produto")
    descricao: str = Field(description="Descrição do produto")
    sku: str = Field(description="Código SKU do produto")
    barcode: str = Field(description="Código de barras EAN-13 do produto")
    ncm: str = Field(description="Código NCM do produto")
    endereco_id: int = Field(description="ID do endereço de armazenagem do produto")
    fornecedor_id: int = Field(description="ID do fornecedor do produto")
    subcategoria_id: int = Field(description="ID da subcategoria do produto")
    estoque_atual: Decimal = Field(description="Estoque atual do produto")
    estoque_min: Decimal = Field(description="Estoque mínimo do produto")
    estoque_max: Decimal = Field(description="Estoque máximo do produto")
    unidade_id: int = Field(description="ID da unidade de medida do produto")
    preco_venda: Decimal = Field(description="Preço de venda do produto")
    preco_custo: Decimal = Field(description="Preço de custo do produto")
    status: bool = Field(description="Status do produto")
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class ProdutoUpdate(BaseModel):
    """Schema utilizado para atualização de um produto.

    :param nome: Nome do produto.
    :type nome: str | None
    :param descricao: Descrição do produto.
    :type descricao: str | None
    :param ncm: Código NCM do produto.
    :type ncm: str | None
    :param endereco_id: ID do endereço de armazenagem do produto.
    :type endereco_id: int | None
    :param subcategoria_id: ID da subcategoria do produto.
    :type subcategoria_id: int | None
    :param estoque_min: Estoque mínimo do produto.
    :type estoque_min: Decimal | None
    :param estoque_max: Estoque máximo do produto.
    :type estoque_max: Decimal | None
    :param preco_venda: Preço de venda do produto.
    :type preco_venda: Decimal | None
    :param preco_custo: Preço de custo do produto.
    :type preco_custo: Decimal | None
    :param status: Status do produto.
    :type status: bool | None
    """

    nome: str | None = Field(
        min_length=5, max_length=50, default=None, description="Nome do produto"
    )
    descricao: str | None = Field(
        min_length=5, max_length=75, default=None, description="Descrição do produto"
    )
    ncm: str | None = Field(
        min_length=8,
        max_length=8,
        default=None,
        pattern=r"^\d{8}$",
        description="Código NCM do produto",
        examples=["61091000", "2202.10.00"],
    )
    endereco_id: int | None = Field(
        default=None, description="ID do endereço de armazenagem do produto"
    )
    subcategoria_id: int | None = Field(
        default=None, description="ID da subcategoria do produto"
    )
    estoque_min: Decimal | None = Field(
        ge=Decimal("0.00"),
        default=None,
        description="Estoque mínimo do produto",
    )
    estoque_max: Decimal | None = Field(
        ge=Decimal("0.00"),
        default=None,
        description="Estoque máximo do produto",
    )
    preco_venda: Decimal | None = Field(
        ge=Decimal("0.00"), default=None, description="Preço de venda do produto"
    )
    preco_custo: Decimal | None = Field(
        ge=Decimal("0.00"), default=None, description="Preço de custo do produto"
    )
    status: bool | None = Field(default=None, description="Status do produto")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("ncm", mode="before")
    @classmethod
    def processar_ncm(cls, valor: Any) -> str | None:
        """Processa e valida o código NCM do produto.

        :param valor: Código NCM do produto a ser processado.
        :type valor: Any
        :return: Código NCM do produto processado ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir exatamente 8 caracteres numéricos.
        """
        if valor is None or valor == "":
            return None

        if not isinstance(valor, str):
            raise ValueError("O código NCM do produto deve ser enviado como texto.")

        valor = valor.replace(".", "")

        if not re.fullmatch(pattern=r"\d{8}", string=valor):
            raise ValueError(
                "Código NCM do produto inválido. Deve ter exatamente 8 caracteres numéricos."
            )

        return valor
