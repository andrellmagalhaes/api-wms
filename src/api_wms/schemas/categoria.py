"""Schemas Pydantic utilizados na validação e serialização de categorias."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api_wms.schemas.subcategoria import SubcategoriaResponse


class CategoriaCreate(BaseModel):
    """Schema utilizado para criação de uma categoria.

    :param nome: Nome da categoria.
    :type nome: str
    :param status: Status da categoria.
    :type status: bool
    """

    nome: str = Field(min_length=5, max_length=50, description="Nome da categoria")
    status: bool = Field(default=True, description="Status da categoria")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )


class CategoriaResponse(BaseModel):
    """Schema utilizado para resposta com os dados de uma categoria.

    :param id: ID da categoria.
    :type id: int
    :param nome: Nome da categoria.
    :type nome: str
    :param status: Status da categoria.
    :type status: bool
    :param subcategorias: Lista de subcategorias da categoria.
    :type subcategorias: list[SubcategoriaResponse]
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID da categoria")
    nome: str = Field(description="Nome da categoria")
    status: bool = Field(description="Status da categoria")
    subcategorias: list[SubcategoriaResponse] = Field(
        description="Lista de subcategorias da categoria"
    )
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class CategoriaUpdate(BaseModel):
    """Schema utilizado para atualização de uma categoria de produtos.

    :param nome: Nome da categoria.
    :type nome: str | None
    :param status: Status da categoria.
    :type status: bool | None
    """

    nome: str | None = Field(
        min_length=5,
        max_length=50,
        default=None,
        description="Nome da categoria",
    )
    status: bool | None = Field(default=None, description="Status da categoria")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )
