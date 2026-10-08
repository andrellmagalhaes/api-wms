"""Rotas responsáveis pelas operações de consulta e gerenciamento de fornecedores."""

import re
from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api_wms.database import iniciar_sessao
from api_wms.models.fornecedor import Fornecedor
from api_wms.schemas.fornecedor import (
    FornecedorCreate,
    FornecedorResponse,
    FornecedorUpdate,
)

router: APIRouter = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


@router.get(
    "/{id}",
    response_model=FornecedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca um fornecedor pelo ID",
)
def buscar_fornecedor_id(id: int, sessao: Sessao) -> Fornecedor:
    """Busca um fornecedor pelo ID.

    :param id: ID do fornecedor a ser consultado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Fornecedor encontrado.
    :rtype: Fornecedor
    :raises HTTPException: Se o fornecedor não for encontrado.
    """
    fornecedor: Fornecedor | None = sessao.get(Fornecedor, id)

    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )

    return fornecedor


@router.get(
    "/cnpj/{cnpj}",
    response_model=FornecedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca um fornecedor pelo CNPJ",
)
def buscar_fornecedor_cnpj(cnpj: str, sessao: Sessao) -> Fornecedor:
    """Busca um fornecedor pelo CNPJ.

    :param cnpj: CNPJ do fornecedor a ser consultado.
    :type cnpj: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Fornecedor encontrado.
    :rtype: Fornecedor
    :raises HTTPException: Se o fornecedor não for encontrado.
    """
    fornecedor: Fornecedor | None = sessao.scalar(
        statement=select(Fornecedor).where(
            Fornecedor.cnpj
            == re.sub(pattern=r"[^a-zA-Z0-9]", repl="", string=cnpj).upper()
        )
    )

    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )

    return fornecedor


@router.get(
    "/",
    response_model=list[FornecedorResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista os fornecedores",
)
def listar_fornecedores(
    sessao: Sessao,
    nome: str | None = None,
    email: str | None = None,
    telefone: str | None = None,
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Fornecedor]:
    """Filtra e lista os fornecedores.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome do fornecedor utilizado como filtro.
    :type nome: str | None
    :param email: Endereço de email do fornecedor utilizado como filtro.
    :type email: str | None
    :param telefone: Número de telefone do fornecedor utilizado como filtro.
    :type telefone: str | None
    :param status: Status do fornecedor utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de fornecedores encontrados.
    :rtype: Sequence[Fornecedor]
    """
    comando: Select = select(Fornecedor)

    if nome is not None:
        comando = comando.where(Fornecedor.nome.ilike(f"%{nome}%"))

    if email is not None:
        comando = comando.where(Fornecedor.email.ilike(f"%{email}%"))

    if telefone is not None:
        comando = comando.where(
            Fornecedor.telefone.ilike(
                f"{re.sub(pattern=r'[^0-9]', repl='', string=telefone)}%"
            )
        )

    if status is not None:
        comando = comando.where(Fornecedor.status == status)

    return sessao.scalars(
        statement=comando.options(selectinload(Fornecedor.produtos))
        .order_by(Fornecedor.nome)
        .offset(offset)
        .limit(limit)
    ).all()


@router.post(
    "/",
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo fornecedor",
)
def criar_fornecedor(fornecedor: FornecedorCreate, sessao: Sessao) -> Fornecedor:
    """Cria um novo fornecedor.

    :param fornecedor: Dados do fornecedor a ser criado.
    :type fornecedor: FornecedorCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Fornecedor criado.
    :rtype: Fornecedor
    :raises HTTPException: Se já existir um fornecedor com o mesmo nome ou CNPJ.
    """
    if sessao.scalar(
        statement=select(Fornecedor).where(
            (Fornecedor.nome == fornecedor.nome) | (Fornecedor.cnpj == fornecedor.cnpj)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um fornecedor cadastrado com este nome e/ou CNPJ.",
        )

    novo_fornecedor: Fornecedor = Fornecedor(**fornecedor.model_dump())

    sessao.add(instance=novo_fornecedor)
    sessao.commit()
    sessao.refresh(instance=novo_fornecedor)

    return novo_fornecedor


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um fornecedor pelo ID",
)
def excluir_fornecedor_id(id: int, sessao: Sessao) -> None:
    """Exclui um fornecedor pelo ID.

    :param id: ID do fornecedor a ser excluído.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :raises HTTPException: Se o fornecedor não for encontrado.
    :raises HTTPException: Se existirem produtos vinculados ao fornecedor.
    """
    fornecedor: Fornecedor | None = sessao.get(Fornecedor, id)

    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )

    try:
        sessao.delete(instance=fornecedor)
        sessao.commit()

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o fornecedor. Existem um ou mais produtos vinculados a ele.",
        )


@router.patch(
    "/{id}",
    response_model=FornecedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza um fornecedor pelo ID",
)
def atualizar_fornecedor_id(
    id: int, payload: FornecedorUpdate, sessao: Sessao
) -> Fornecedor:
    """Atualiza um fornecedor pelo ID.

    :param id: ID do fornecedor a ser atualizado.
    :type id: int
    :param payload: Dados do fornecedor a serem atualizados.
    :type payload: FornecedorUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Fornecedor atualizado.
    :rtype: Fornecedor
    :raises HTTPException: Se o fornecedor não for encontrado.
    :raises HTTPException: Se já existir outro fornecedor com o mesmo nome.
    """
    fornecedor: Fornecedor | None = sessao.get(Fornecedor, id)

    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado."
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return fornecedor

    if "nome" in update_data and sessao.scalar(
        statement=select(Fornecedor).where(
            (Fornecedor.nome == update_data["nome"]) & (Fornecedor.id != id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um fornecedor cadastrado com este nome.",
        )

    for atributo, valor in update_data.items():
        setattr(fornecedor, atributo, valor)

    sessao.commit()
    sessao.refresh(fornecedor)

    return fornecedor
