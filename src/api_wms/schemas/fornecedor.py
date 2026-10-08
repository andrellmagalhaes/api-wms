"""Schemas Pydantic utilizados na validação e serialização de fornecedores."""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api_wms.schemas.produto import ProdutoResponse


class FornecedorCreate(BaseModel):
    """Schema utilizado para criação de um fornecedor.

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
    """

    nome: str = Field(min_length=5, max_length=50, description="Nome do fornecedor")
    cnpj: str = Field(
        min_length=14,
        max_length=14,
        pattern=r"^[A-Z0-9]{14}$",
        description="CNPJ do fornecedor",
        examples=["12345678000195", "12.ABC.345/0001-95"],
    )
    email: str | None = Field(
        min_length=6,
        max_length=50,
        default=None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Endereço de email do fornecedor",
        examples=["contato@fornecedor.com.br", "vendas-sp@empresa.com"],
    )
    telefone: str | None = Field(
        min_length=10,
        max_length=11,
        default=None,
        pattern=r"^[1-9]{2}\d{8,9}$",
        description="Número de telefone do fornecedor",
        examples=["7112345678", "71987654321", "(71) 98765-4321"],
    )
    status: bool = Field(default=True, description="Status do fornecedor")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("cnpj", mode="before")
    @classmethod
    def processar_cnpj(cls, valor: Any) -> str:
        """Processa e valida o CNPJ do fornecedor.

        :param valor: CNPJ do fornecedor a ser processado.
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

    @field_validator("email", mode="before")
    @classmethod
    def processar_email(cls, valor: Any) -> str | None:
        """Processa e valida o endereço de email do fornecedor.

        :param valor: Endereço de email do fornecedor a ser processado.
        :type valor: Any
        :return: Endereço de email do fornecedor processado ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir um formato de email válido.
        """
        if valor is None or valor == "":
            return None

        if not isinstance(valor, str):
            raise ValueError(
                "O endereço de email do fornecedor deve ser enviado como texto."
            )

        valor = valor.lower()

        if not re.fullmatch(
            pattern=r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", string=valor
        ):
            raise ValueError("Endereço de email do fornecedor inválido.")

        return valor

    @field_validator("telefone", mode="before")
    @classmethod
    def processar_telefone(cls, valor: Any) -> str | None:
        """Processa e valida o número de telefone do fornecedor.

        :param valor: Número de telefone do fornecedor a ser processado.
        :type valor: Any
        :return: Número de telefone do fornecedor processado ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir 10 ou 11 caracteres numéricos válidos.
        """
        if valor is None or valor == "":
            return None

        if not isinstance(valor, str):
            raise ValueError(
                "O número de telefone do fornecedor deve ser enviado como texto."
            )

        valor = (
            valor.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        )

        if not re.fullmatch(pattern=r"[1-9]{2}\d{8,9}", string=valor):
            raise ValueError(
                "Número de telefone do fornecedor inválido. Deve ter 10 ou 11 caracteres numéricos, sendo os dois primeiros do DDD."
            )

        return valor


class FornecedorResponse(BaseModel):
    """Schema utilizado para resposta com os dados de um fornecedor.

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
    :param produtos: Lista de produtos distribuídos pelo fornecedor.
    :type produtos: list[ProdutoResponse]
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID do fornecedor")
    nome: str = Field(description="Nome do fornecedor")
    cnpj: str = Field(description="CNPJ do fornecedor")
    email: str | None = Field(description="Endereço de email do fornecedor")
    telefone: str | None = Field(description="Número de telefone do fornecedor")
    status: bool = Field(description="Status do fornecedor")
    produtos: list[ProdutoResponse] = Field(
        description="Lista de produtos distribuídos pelo fornecedor"
    )
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class FornecedorUpdate(BaseModel):
    """Schema utilizado para atualização de um fornecedor.

    :param nome: Nome do fornecedor.
    :type nome: str | None
    :param email: Endereço de email do fornecedor.
    :type email: str | None
    :param telefone: Número de telefone do fornecedor.
    :type telefone: str | None
    :param status: Status do fornecedor.
    :type status: bool | None
    """

    nome: str | None = Field(
        min_length=5, max_length=50, default=None, description="Nome do fornecedor"
    )
    email: str | None = Field(
        min_length=6,
        max_length=50,
        default=None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Endereço de email do fornecedor",
        examples=["contato@fornecedor.com.br", "vendas-sp@empresa.com"],
    )
    telefone: str | None = Field(
        min_length=10,
        max_length=11,
        default=None,
        pattern=r"^[1-9]{2}\d{8,9}$",
        description="Número de telefone do fornecedor",
        examples=["7112345678", "71987654321", "(71) 98765-4321"],
    )
    status: bool | None = Field(default=None, description="Status do fornecedor")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )

    @field_validator("email", mode="before")
    @classmethod
    def processar_email(cls, valor: Any) -> str | None:
        """Processa e valida o endereço de email do fornecedor.

        :param valor: Endereço de email do fornecedor a ser processado.
        :type valor: Any
        :return: Endereço de email do fornecedor processado ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir um formato de email válido.
        """
        if valor is None or valor == "":
            return None

        if not isinstance(valor, str):
            raise ValueError(
                "O endereço de email do fornecedor deve ser enviado como texto."
            )

        valor = valor.lower()

        if not re.fullmatch(
            pattern=r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", string=valor
        ):
            raise ValueError("Endereço de email do fornecedor inválido.")

        return valor

    @field_validator("telefone", mode="before")
    @classmethod
    def processar_telefone(cls, valor: Any) -> str | None:
        """Processa e valida o número de telefone do fornecedor.

        :param valor: Número de telefone do fornecedor a ser processado.
        :type valor: Any
        :return: Número de telefone do fornecedor processado ou None.
        :rtype: str | None
        :raises ValueError: Se o valor não for uma string ou não possuir 10 ou 11 caracteres numéricos válidos.
        """
        if valor is None or valor == "":
            return None

        if not isinstance(valor, str):
            raise ValueError(
                "O número de telefone do fornecedor deve ser enviado como texto."
            )

        valor = (
            valor.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        )

        if not re.fullmatch(pattern=r"[1-9]{2}\d{8,9}", string=valor):
            raise ValueError(
                "Número de telefone do fornecedor inválido. Deve ter 10 ou 11 caracteres numéricos, sendo os dois primeiros do DDD."
            )

        return valor
