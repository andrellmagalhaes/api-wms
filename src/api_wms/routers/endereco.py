"""Rotas responsáveis pelas operações de consulta e gerenciamento de endereços de armazenagem."""

from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from api_wms.database import iniciar_sessao
from api_wms.models.endereco import Endereco
from api_wms.schemas.endereco import (
    EnderecoCreate,
    EnderecoResponse,
    EnderecoUpdate,
)

router: APIRouter = APIRouter(prefix="/enderecos", tags=["Enderecos"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


@router.get(
    "/{id}",
    response_model=EnderecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca um endereço de armazenagem pelo ID",
)
def buscar_endereco_armazenagem_id(id: int, sessao: Sessao) -> Endereco:
    """Busca um endereço de armazenagem pelo ID.

    :param id: ID do endereço de armazenagem a ser consultado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Endereço de armazenagem encontrado.
    :rtype: Endereco
    :raises HTTPException: Se o endereço de armazenagem não for encontrado.
    """
    endereco: Endereco | None = sessao.get(Endereco, id)

    if endereco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço de armazenagem não encontrado.",
        )

    return endereco


@router.get(
    "/cea/{cea}",
    response_model=EnderecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca um endereço de armazenagem pelo código (CEA)",
)
def buscar_endereco_armazenagem_cea(cea: str, sessao: Sessao) -> Endereco:
    """Busca um endereço de armazenagem pelo código (CEA).

    :param cea: Código do endereço de armazenagem a ser consultado.
    :type cea: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Endereço de armazenagem encontrado.
    :rtype: Endereco
    :raises HTTPException: Se o endereço de armazenagem não for encontrado.
    """
    endereco: Endereco | None = sessao.scalar(
        select(Endereco).where(Endereco.cea == cea)
    )

    if endereco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço de armazenagem não encontrado.",
        )

    return endereco


@router.get(
    "/",
    response_model=list[EnderecoResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista os endereços de armazenagem",
)
def listar_enderecos_armazenagem(
    sessao: Sessao,
    cea: str | None = None,
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Endereco]:
    """Filtra e lista os endereços de armazenagem.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param cea: Código do endereço de armazenagem utilizado como filtro.
    :type cea: str | None
    :param status: Status do endereço de armazenagem utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de endereços de armazenagem encontrados.
    :rtype: Sequence[Endereco]
    """
    comando: Select = select(Endereco)

    if cea is not None:
        comando = comando.where(Endereco.cea.like(f"{cea}%"))

    if status is not None:
        comando = comando.where(Endereco.status == status)

    return sessao.scalars(
        statement=comando.options(joinedload(Endereco.produto))
        .order_by(Endereco.cea)
        .offset(offset)
        .limit(limit)
    ).all()


@router.post(
    "/",
    response_model=EnderecoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo endereço de armazenagem",
)
def criar_endereco_armazenagem(endereco: EnderecoCreate, sessao: Sessao) -> Endereco:
    """Cria um novo endereço de armazenagem.

    :param endereco: Dados do endereço de armazenagem a ser criado.
    :type endereco: EnderecoCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Endereço de armazenagem criado.
    :rtype: Endereco
    :raises HTTPException: Se já existir um endereço de armazenagem com o mesmo código (CEA).
    """
    if sessao.scalar(statement=select(Endereco).where((Endereco.cea == endereco.cea))):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um endereço de armazenagem cadastrado com este código (CEA).",
        )

    novo_endereco: Endereco = Endereco(**endereco.model_dump())

    sessao.add(instance=novo_endereco)
    sessao.commit()
    sessao.refresh(instance=novo_endereco)

    return novo_endereco


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um endereço de armazenagem pelo ID",
)
def excluir_endereco_armazenagem_id(id: int, sessao: Sessao) -> None:
    """Exclui um endereço de armazenagem pelo ID.

    :param id: ID do endereço de armazenagem a ser excluído.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :raises HTTPException: Se o endereço de armazenagem não for encontrado.
    :raises HTTPException: Se existir um produto vinculado ao endereço de armazenagem.
    """
    endereco: Endereco | None = sessao.get(Endereco, id)

    if endereco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço de armazenagem não encontrado.",
        )

    try:
        sessao.delete(instance=endereco)
        sessao.commit()

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o endereço de armazenagem. Existe um produto vinculado a ele.",
        )


@router.patch(
    "/{id}",
    response_model=EnderecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza um endereço de armazenagem pelo ID",
)
def atualizar_endereco_armazenagem_id(
    id: int, payload: EnderecoUpdate, sessao: Sessao
) -> Endereco:
    """Atualiza um endereço de armazenagem pelo ID.

    :param id: ID do endereço de armazenagem a ser atualizado.
    :type id: int
    :param payload: Dados do endereço de armazenagem a serem atualizados.
    :type payload: EnderecoUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Endereço de armazenagem atualizado.
    :rtype: Endereco
    :raises HTTPException: Se o endereço de armazenagem não for encontrado.
    :raises HTTPException: Se já existir outro endereço de armazenagem com o mesmo código (CEA).
    """
    endereco: Endereco | None = sessao.get(Endereco, id)

    if not endereco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço de armazenagem não encontrado.",
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return endereco

    if "cea" in update_data and sessao.scalar(
        statement=select(Endereco).where(
            (Endereco.cea == update_data["cea"]) & (Endereco.id != id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um endereço de armazenagem cadastrado com este código (CEA).",
        )

    for atributo, valor in update_data.items():
        setattr(endereco, atributo, valor)

    sessao.commit()
    sessao.refresh(endereco)

    return endereco
