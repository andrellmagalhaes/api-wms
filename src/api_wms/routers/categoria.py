"""Rotas responsáveis pelas operações de consulta e gerenciamento de categorias de produto."""

from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api_wms.database import iniciar_sessao
from api_wms.models.categoria import Categoria
from api_wms.schemas.categoria import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
)

router: APIRouter = APIRouter(prefix="/categorias", tags=["Categorias"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


@router.get(
    "/{id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca uma categoria de produto pelo ID",
)
def buscar_categoria_produto_id(id: int, sessao: Sessao) -> Categoria:
    """Busca uma categoria de produto pelo ID.

    :param id: ID da categoria de produto a ser consultada.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Categoria de produto encontrada.
    :rtype: Categoria
    :raises HTTPException: Se a categoria de produto não for encontrada.
    """
    categoria: Categoria | None = sessao.get(Categoria, id)

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria de produto não encontrada.",
        )

    return categoria


@router.get(
    "/",
    response_model=list[CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista as categorias de produto",
)
def listar_categorias_produto(
    sessao: Sessao,
    nome: str | None = None,
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Categoria]:
    """Filtra e lista as categorias de produto.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome da categoria de produto utilizado como filtro.
    :type nome: str | None
    :param status: Status da categoria de produto utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de categorias de produtos encontradas.
    :rtype: Sequence[Categoria]
    """
    comando: Select = select(Categoria)

    if nome is not None:
        comando = comando.where(Categoria.nome.ilike(f"%{nome}%"))

    if status is not None:
        comando = comando.where(Categoria.status == status)

    return sessao.scalars(
        statement=comando.options(selectinload(Categoria.subcategorias))
        .order_by(Categoria.nome)
        .offset(offset)
        .limit(limit)
    ).all()


@router.post(
    "/",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova categoria de produto",
)
def criar_categoria_produto(categoria: CategoriaCreate, sessao: Sessao) -> Categoria:
    """Cria uma nova categoria de produto.

    :param categoria: Dados da categoria de produto a ser criada.
    :type categoria: CategoriaCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Categoria de produto criada.
    :rtype: Categoria
    :raises HTTPException: Se já existir uma categoria de produto com o mesmo nome.
    """
    if sessao.scalar(
        statement=select(Categoria).where((Categoria.nome == categoria.nome))
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria de produto cadastrada com este nome.",
        )

    nova_categoria: Categoria = Categoria(**categoria.model_dump())

    sessao.add(instance=nova_categoria)
    sessao.commit()
    sessao.refresh(instance=nova_categoria)

    return nova_categoria


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma categoria de produto pelo ID",
)
def excluir_categoria_produto_id(id: int, sessao: Sessao) -> None:
    """Exclui uma categoria de produto pelo ID.

    :param id: ID da categoria de produto a ser excluída.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :raises HTTPException: Se a categoria de produto não for encontrada.
    :raises HTTPException: Se existirem subcategorias de produtos vinculadas à categoria.
    """
    categoria: Categoria | None = sessao.get(Categoria, id)

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria de produto não encontrada.",
        )

    try:
        sessao.delete(instance=categoria)
        sessao.commit()

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir a categoria de produto. Existem um ou mais subcategorias de produto vinculadas a ela.",
        )


@router.patch(
    "/{id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza uma categoria de produto pelo ID",
)
def atualizar_categoria_produto_id(
    id: int, payload: CategoriaUpdate, sessao: Sessao
) -> Categoria:
    """Atualiza uma categoria de produto pelo ID.

    :param id: ID da categoria de produto a ser atualizada.
    :type id: int
    :param payload: Dados da categoria de produto a serem atualizados.
    :type payload: CategoriaUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Categoria de produto atualizada.
    :rtype: Categoria
    :raises HTTPException: Se a categoria de produto não for encontrada.
    :raises HTTPException: Se já existir outra categoria de produto com o mesmo nome.
    """
    categoria: Categoria | None = sessao.get(Categoria, id)

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria de produto não encontrada.",
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return categoria

    if "nome" in update_data and sessao.scalar(
        statement=select(Categoria).where(
            (Categoria.nome == update_data["nome"]) & (Categoria.id != id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria de produto cadastrada com este nome.",
        )

    for atributo, valor in update_data.items():
        setattr(categoria, atributo, valor)

    sessao.commit()
    sessao.refresh(categoria)

    return categoria
