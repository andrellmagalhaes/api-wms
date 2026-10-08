"""Rotas responsáveis pelas operações de consulta e gerenciamento de unidades de medida."""

from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api_wms.database import iniciar_sessao
from api_wms.models.unidade import Unidade
from api_wms.schemas.unidade import UnidadeCreate, UnidadeResponse, UnidadeUpdate

router: APIRouter = APIRouter(prefix="/unidades", tags=["Unidades"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


@router.get(
    "/{id}",
    response_model=UnidadeResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca uma unidade de medida pelo ID",
)
def buscar_unidade_medida_id(id: int, sessao: Sessao) -> Unidade:
    """Busca uma unidade de medida pelo ID.

    :param id: ID da unidade de medida a ser consultada.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Unidade de medida encontrada.
    :rtype: Unidade
    :raises HTTPException: Se a unidade de medida não for encontrada.
    """
    unidade: Unidade | None = sessao.get(Unidade, id)

    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade de medida não encontrada.",
        )

    return unidade


@router.get(
    "/",
    response_model=list[UnidadeResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista as unidades de medida",
)
def listar_unidades_medida(
    sessao: Sessao,
    nome: str | None = None,
    sigla: str | None = None,
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Unidade]:
    """Filtra e lista as unidades de medida.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome da unidade de medida utilizado como filtro.
    :type nome: str | None
    :param sigla: Sigla da unidade de medida utilizada como filtro.
    :type sigla: str | None
    :param status: Status da unidade de medida utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de unidades de medida encontradas.
    :rtype: Sequence[Unidade]
    """
    comando: Select = select(Unidade)

    if nome is not None:
        comando = comando.where(Unidade.nome.ilike(f"%{nome}%"))

    if sigla is not None:
        comando = comando.where(Unidade.sigla.ilike(f"{sigla}%"))

    if status is not None:
        comando = comando.where(Unidade.status == status)

    return sessao.scalars(
        statement=comando.order_by(Unidade.nome).offset(offset).limit(limit)
    ).all()


@router.post(
    "/",
    response_model=UnidadeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova unidade de medida",
)
def criar_unidade_medida(unidade: UnidadeCreate, sessao: Sessao) -> Unidade:
    """Cria uma nova unidade de medida.

    :param unidade: Dados da unidade de medida a ser criada.
    :type unidade: UnidadeCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Unidade de medida criada.
    :rtype: Unidade
    :raises HTTPException: Se já existir uma unidade de medida com o mesmo nome ou sigla.
    """
    if sessao.scalar(
        statement=select(Unidade).where(
            (Unidade.nome == unidade.nome) | (Unidade.sigla == unidade.sigla)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma unidade de medida cadastrada com este nome e/ou sigla.",
        )

    nova_unidade: Unidade = Unidade(**unidade.model_dump())

    sessao.add(instance=nova_unidade)
    sessao.commit()
    sessao.refresh(instance=nova_unidade)

    return nova_unidade


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma unidade de medida pelo ID",
)
def excluir_unidade_medida_id(id: int, sessao: Sessao) -> None:
    """Exclui uma unidade de medida pelo ID.

    :param id: ID da unidade de medida a ser excluída.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :raises HTTPException: Se a unidade de medida não for encontrada.
    :raises HTTPException: Se existirem produtos vinculados à unidade de medida.
    """
    unidade: Unidade | None = sessao.get(Unidade, id)

    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade de medida não encontrada.",
        )

    try:
        sessao.delete(instance=unidade)
        sessao.commit()

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir a unidade de medida. Existem um ou mais produtos vinculados a ela.",
        )


@router.patch(
    "/{id}",
    response_model=UnidadeResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza uma unidade de medida pelo ID",
)
def atualizar_unidade_medida_id(
    id: int, payload: UnidadeUpdate, sessao: Sessao
) -> Unidade:
    """Atualiza uma unidade de medida pelo ID.

    :param id: ID da unidade de medida a ser atualizada.
    :type id: int
    :param payload: Dados da unidade de medida a serem atualizados.
    :type payload: UnidadeUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Unidade de medida atualizada.
    :rtype: Unidade
    :raises HTTPException: Se a unidade de medida não for encontrada.
    :raises HTTPException: Se já existir outra unidade de medida com o mesmo nome ou sigla.
    """
    unidade: Unidade | None = sessao.get(Unidade, id)

    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade de medida não encontrada.",
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return unidade

    if any(atributo in update_data for atributo in ["nome", "sigla"]):
        if sessao.scalar(
            statement=select(Unidade).where(
                (
                    (Unidade.nome == update_data.get("nome", unidade.nome))
                    | (Unidade.sigla == update_data.get("sigla", unidade.sigla))
                )
                & (Unidade.id != id)
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma unidade de medida cadastrada com este nome e/ou sigla.",
            )

    for atributo, valor in update_data.items():
        setattr(unidade, atributo, valor)

    sessao.commit()
    sessao.refresh(unidade)

    return unidade
