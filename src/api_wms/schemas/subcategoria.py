"""Schemas Pydantic utilizados na validação e serialização de subcategorias."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubcategoriaCreate(BaseModel):
    """Schema utilizado para criação de uma subcategoria.

    :param nome: Nome da subcategoria.
    :type nome: str
    :param categoria_id: ID da categoria referente à subcategoria.
    :type categoria_id: int
    :param status: Status da subcategoria.
    :type status: bool
    """

    nome: str = Field(min_length=5, max_length=50, description="Nome da subcategoria")
    categoria_id: int = Field(description="ID da categoria referente à subcategoria")
    status: bool = Field(default=True, description="Status da subcategoria")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )


class SubcategoriaResponse(BaseModel):
    """Schema utilizado para resposta com os dados de uma subcategoria.

    :param id: ID da subcategoria.
    :type id: int
    :param nome: Nome da subcategoria.
    :type nome: str
    :param categoria_id: ID da categoria referente à subcategoria.
    :type categoria_id: int
    :param status: Status da subcategoria.
    :type status: bool
    :param criado_em: Data e hora de criação do registro.
    :type criado_em: datetime
    :param atualizado_em: Data e hora de atualização do registro.
    :type atualizado_em: datetime
    """

    id: int = Field(description="ID da subcategoria")
    nome: str = Field(description="Nome da subcategoria")
    categoria_id: int = Field(description="ID da categoria referente à subcategoria")
    status: bool = Field(description="Status da subcategoria")
    criado_em: datetime = Field(description="Data e hora de criação do registro")
    atualizado_em: datetime = Field(
        description="Data e hora de atualização do registro"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)


class SubcategoriaUpdate(BaseModel):
    """Schema utilizado para atualização de uma subcategoria.

    :param nome: Nome da subcategoria.
    :type nome: str | None
    :param status: Status da subcategoria.
    :type status: bool | None
    """

    nome: str | None = Field(
        min_length=5,
        max_length=50,
        default=None,
        description="Nome da subcategoria",
    )
    status: bool | None = Field(default=None, description="Status da subcategoria")

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=False,
        strict=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=False,
        populate_by_name=False,
    )
