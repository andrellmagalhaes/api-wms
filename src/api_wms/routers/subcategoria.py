"""Rotas responsáveis pelas operações de consulta e gerenciamento de subcategorias de produto."""

from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api_wms.database import iniciar_sessao
from api_wms.models.categoria import Categoria
from api_wms.models.subcategoria import Subcategoria
from api_wms.schemas.subcategoria import (
    SubcategoriaCreate,
    SubcategoriaResponse,
    SubcategoriaUpdate,
)

router: APIRouter = APIRouter(prefix="/subcategorias", tags=["Subcategorias"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


@router.get(
    "/{id}",
    response_model=SubcategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca uma subcategoria de produto pelo ID",
)
def buscar_subcategoria_produto_id(id: int, sessao: Sessao) -> Subcategoria:
    """Busca uma subcategoria de produto pelo ID.

    :param id: ID da subcategoria de produto a ser consultada.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Subcategoria de produto encontrada.
    :rtype: Subcategoria
    :raises HTTPException: Se a subcategoria de produto não for encontrada.
    """
    subcategoria: Subcategoria | None = sessao.get(Subcategoria, id)

    if subcategoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria de produto não encontrada.",
        )

    return subcategoria


@router.get(
    "/",
    response_model=list[SubcategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista as subcategorias de produto",
)
def listar_subcategorias_produto(
    sessao: Sessao,
    nome: str | None = None,
    categoria_id: int | None = Query(default=None, alias="categoria"),
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Subcategoria]:
    """Filtra e lista as subcategorias de produto.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome da subcategoria de produto utilizado como filtro.
    :type nome: str | None
    :param categoria_id: ID da categoria de produto utilizada como filtro.
    :type categoria_id: int | None
    :param status: Status da subcategoria de produto utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de subcategorias de produtos encontradas.
    :rtype: Sequence[Subcategoria]
    """
    comando: Select = select(Subcategoria)

    if nome is not None:
        comando = comando.where(Subcategoria.nome.ilike(f"%{nome}%"))

    if categoria_id is not None:
        comando = comando.where(Subcategoria.categoria_id == categoria_id)

    if status is not None:
        comando = comando.where(Subcategoria.status == status)

    return sessao.scalars(
        statement=comando.order_by(Subcategoria.nome).offset(offset).limit(limit)
    ).all()


@router.post(
    "/",
    response_model=SubcategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova subcategoria de produto",
)
def criar_subcategoria_produto(
    subcategoria: SubcategoriaCreate, sessao: Sessao
) -> Subcategoria:
    """Cria uma nova subcategoria de produto.

    :param subcategoria: Dados da subcategoria de produto a ser criada.
    :type subcategoria: SubcategoriaCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Subcategoria de produto criada.
    :rtype: Subcategoria
    :raises HTTPException: Se a categoria de produto não for encontrada.
    :raises HTTPException: Se a categoria de produto estiver inativa.
    :raises HTTPException: Se já existir uma subcategoria de produto com o mesmo nome associada à categoria de produto escolhida.
    """
    categoria: Categoria | None = sessao.scalar(
        statement=select(Categoria).where(Categoria.id == subcategoria.categoria_id)
    )
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Categoria de produto não encontrada.",
        )

    if not categoria.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Categoria de produto inativa."
        )

    if sessao.scalar(
        statement=select(Subcategoria).where(
            (Subcategoria.nome == subcategoria.nome)
            & (Subcategoria.categoria_id == subcategoria.categoria_id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma subcategoria de produto cadastrada com este nome associada à categoria de produto escolhida.",
        )

    nova_subcategoria: Subcategoria = Subcategoria(**subcategoria.model_dump())

    sessao.add(instance=nova_subcategoria)
    sessao.commit()
    sessao.refresh(instance=nova_subcategoria)

    return nova_subcategoria


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma subcategoria de produto pelo ID",
)
def excluir_subcategoria_produto_id(id: int, sessao: Sessao) -> None:
    """Exclui uma subcategoria de produto pelo ID.

    :param id: ID da subcategoria de produto a ser excluída.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :raises HTTPException: Se a subcategoria de produto não for encontrada.
    :raises HTTPException: Se existirem produtos vinculados à subcategoria de produto.
    """
    subcategoria: Subcategoria | None = sessao.get(Subcategoria, id)

    if subcategoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria de produto não encontrada.",
        )

    try:
        sessao.delete(instance=subcategoria)
        sessao.commit()

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir a subcategoria de produto. Existem um ou mais produtos vinculados a ela.",
        )


@router.patch(
    "/{id}",
    response_model=SubcategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza uma subcategoria de produto pelo ID",
)
def atualizar_subcategoria_produto_id(
    id: int, payload: SubcategoriaUpdate, sessao: Sessao
) -> Subcategoria:
    """Atualiza uma subcategoria de produto pelo ID.

    :param id: ID da subcategoria de produto a ser atualizada.
    :type id: int
    :param payload: Dados da subcategoria de produto a serem atualizados.
    :type payload: SubcategoriaUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Subcategoria de produto atualizada.
    :rtype: Subcategoria
    :raises HTTPException: Se a subcategoria de produto não for encontrada.
    :raises HTTPException: Se já existir outra subcategoria de produto com o mesmo nome associada à categoria de produto atual.
    """
    subcategoria: Subcategoria | None = sessao.get(Subcategoria, id)

    if not subcategoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria de produto não encontrada.",
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return subcategoria

    if "nome" in update_data and sessao.scalar(
        statement=select(Subcategoria).where(
            (Subcategoria.nome == update_data["nome"])
            & (Subcategoria.categoria_id == subcategoria.categoria_id)
            & (Subcategoria.id != id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma subcategoria de produto cadastrada com este nome associada à categoria de produto atual.",
        )

    for atributo, valor in update_data.items():
        setattr(subcategoria, atributo, valor)

    sessao.commit()
    sessao.refresh(subcategoria)

    return subcategoria
