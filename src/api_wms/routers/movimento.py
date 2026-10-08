"""Rotas responsáveis pelas operações de consulta, criação e exportação de movimentos de entrada e saída de produtos."""

import csv
from collections.abc import Sequence
from datetime import date
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import Date, Row, RowMapping, Select, cast, func, select
from sqlalchemy.orm import Session, selectinload

from api_wms.database import iniciar_sessao
from api_wms.filtros.movimento import FiltrosMovimento
from api_wms.models.fornecedor import Fornecedor
from api_wms.models.item import Item
from api_wms.models.movimento import Movimento
from api_wms.models.produto import Produto
from api_wms.schemas.movimento import (
    MovimentoCreate,
    MovimentoDetalhesResponse,
    MovimentoResumoResponse,
)
from api_wms.utils import formatar_data

router: APIRouter = APIRouter(prefix="/movimentos", tags=["Movimentos"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


def _filtrar_movimentos(comando: Select, filtros: FiltrosMovimento) -> Select:
    """Aplica os filtros informados à consulta de movimentos.

    :param comando: Comando SQL utilizado para consulta dos movimentos.
    :type comando: Select
    :param filtros: Filtros utilizados para restringir os movimentos consultados.
    :type filtros: FiltrosMovimento
    :return: Comando SQL com os filtros aplicados.
    :rtype: Select
    """
    if filtros.tipo is not None:
        comando = comando.where(Movimento.tipo.ilike(f"{filtros.tipo}%"))

    if filtros.data_min is not None:
        comando = comando.where(cast(Movimento.criado_em, Date) >= filtros.data_min)

    if filtros.data_max is not None:
        comando = comando.where(cast(Movimento.criado_em, Date) <= filtros.data_max)

    if filtros.fornecedor_id is not None:
        comando = comando.where(Movimento.fornecedor_id == filtros.fornecedor_id)

    return comando


@router.get(
    "/",
    response_model=list[MovimentoResumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtra e lista os movimentos",
)
def listar_movimentos(
    sessao: Sessao,
    tipo: str | None = None,
    data_min: date | None = None,
    data_max: date | None = None,
    fornecedor_id: int | None = Query(default=None, alias="fornecedor"),
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Row]:
    """Filtra e lista os movimentos.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param tipo: Tipo do movimento utilizado como filtro.
    :type tipo: str | None
    :param data_min: Data inicial do período utilizada como filtro.
    :type data_min: date | None
    :param data_max: Data final do período utilizada como filtro.
    :type data_max: date | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de movimentos encontrados.
    :rtype: Sequence[Row]
    """
    filtros: FiltrosMovimento = FiltrosMovimento(
        tipo=tipo,
        data_min=data_min,
        data_max=data_max,
        fornecedor_id=fornecedor_id,
    )

    comando: Select = (
        select(
            Movimento.id,
            Movimento.nf_numero,
            Movimento.nf_chave,
            Movimento.tipo,
            Movimento.criado_em,
            Movimento.fornecedor_id,
            func.count(Item.id).label("qtd_itens"),
            func.coalesce(func.sum(Item.qtd_unidades), 0).label("qtd_unidades"),
            func.coalesce(func.sum(Item.qtd_unidades * Item.preco_unit), 0).label(
                "valor_total"
            ),
        )
        .outerjoin(Item, Movimento.id == Item.movimento_id)
        .group_by(Movimento.id)
    )
    comando = _filtrar_movimentos(comando=comando, filtros=filtros)

    return sessao.execute(
        statement=comando.order_by(Movimento.criado_em).offset(offset).limit(limit)
    ).all()


@router.get(
    "/exportar",
    status_code=status.HTTP_200_OK,
    summary="Exporta um relatório dos movimentos em formato CSV",
)
def exportar_relatorio_movimentos(
    sessao: Sessao,
    tipo: str | None = None,
    data_min: date | None = None,
    data_max: date | None = None,
    fornecedor_id: int | None = Query(default=None, alias="fornecedor"),
) -> Response:
    """Exporta um relatório dos movimentos em formato CSV.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param tipo: Tipo do movimento utilizado como filtro.
    :type tipo: str | None
    :param data_min: Data inicial do período utilizada como filtro.
    :type data_min: date | None
    :param data_max: Data final do período utilizada como filtro.
    :type data_max: date | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    :return: Resposta HTTP contendo o relatório dos movimentos em formato CSV.
    :rtype: Response
    :raises HTTPException: Se não houver movimentos que correspondam aos filtros fornecidos.
    """
    filtros: FiltrosMovimento = FiltrosMovimento(
        tipo=tipo,
        data_min=data_min,
        data_max=data_max,
        fornecedor_id=fornecedor_id,
    )

    comando: Select = (
        select(
            Movimento.id,
            Movimento.nf_numero,
            Movimento.nf_chave,
            Movimento.tipo,
            Movimento.criado_em,
            Fornecedor.nome.label("fornecedor_nome"),
            func.count(Item.id).label("qtd_itens"),
            func.coalesce(func.sum(Item.qtd_unidades), 0).label("qtd_unidades"),
            func.coalesce(func.sum(Item.qtd_unidades * Item.preco_unit), 0).label(
                "valor_total"
            ),
        )
        .join(Fornecedor, Movimento.fornecedor_id == Fornecedor.id)
        .outerjoin(Item, Movimento.id == Item.movimento_id)
        .group_by(Movimento.id, Fornecedor.nome)
    )
    comando = _filtrar_movimentos(comando=comando, filtros=filtros)

    movimentos: Sequence[RowMapping] = (
        sessao.execute(statement=comando.order_by(Movimento.criado_em)).mappings().all()
    )

    if not movimentos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não há movimentos que correspondam aos filtros fornecidos.",
        )

    memoria: StringIO = StringIO()
    writer = csv.writer(memoria, delimiter=";")

    writer.writerow(
        [
            "id",
            "nf_numero",
            "nf_chave",
            "tipo",
            "data",
            "fornecedor",
            "qtd_itens",
            "qtd_unidades",
            "valor_total",
        ]
    )

    for movimento in movimentos:
        writer.writerow(
            [
                movimento["id"],
                movimento["nf_numero"],
                movimento["nf_chave"],
                movimento["tipo"],
                formatar_data(data=movimento["criado_em"]),
                movimento["fornecedor_nome"],
                movimento["qtd_itens"],
                movimento["qtd_unidades"],
                movimento["valor_total"],
            ]
        )

    return Response(
        content=memoria.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=movimentos.csv"},
    )


@router.get(
    "/chave/{nf_chave}",
    response_model=MovimentoResumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca o resumo de um movimento pela chave de acesso da nota fiscal",
)
def buscar_resumo_movimento_nf_chave(nf_chave: str, sessao: Sessao) -> Movimento:
    """Busca o resumo de um movimento pela chave de acesso da nota fiscal.

    :param nf_chave: Chave de acesso da nota fiscal do movimento a ser consultado.
    :type nf_chave: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Movimento encontrado.
    :rtype: Movimento
    :raises HTTPException: Se o movimento não for encontrado.
    """
    movimento: Movimento | None = sessao.scalar(
        select(Movimento)
        .where(Movimento.nf_chave == nf_chave)
        .options(selectinload(Movimento.itens))
    )

    if movimento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    return movimento


@router.get(
    "/chave/{nf_chave}/detalhes",
    response_model=MovimentoDetalhesResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca os detalhes de um movimento pela chave de acesso da nota fiscal",
)
def buscar_detalhes_movimento_nf_chave(nf_chave: str, sessao: Sessao) -> Movimento:
    """Busca os detalhes de um movimento pela chave de acesso da nota fiscal.

    :param nf_chave: Chave de acesso da nota fiscal do movimento a ser consultado.
    :type nf_chave: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Movimento encontrado com seus itens.
    :rtype: Movimento
    :raises HTTPException: Se o movimento não for encontrado.
    """
    movimento: Movimento | None = sessao.scalar(
        select(Movimento)
        .where(Movimento.nf_chave == nf_chave)
        .options(selectinload(Movimento.itens))
    )

    if movimento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    return movimento


@router.get(
    "/chave/{nf_chave}/detalhes/exportar",
    status_code=status.HTTP_200_OK,
    summary="Exporta um relatório dos itens de um movimento em formato CSV pela chave de acesso da nota fiscal",
)
def exportar_relatorio_itens_movimento_nf_chave(
    nf_chave: str, sessao: Sessao
) -> Response:
    """Exporta um relatório dos itens de um movimento em formato CSV pela chave de acesso da nota fiscal.

    :param nf_chave: Chave de acesso da nota fiscal do movimento a ser exportado.
    :type nf_chave: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Resposta HTTP contendo o relatório dos itens do movimento em formato CSV.
    :rtype: Response
    :raises HTTPException: Se o movimento não for encontrado.
    """
    if not sessao.scalar(select(Movimento).where(Movimento.nf_chave == nf_chave)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    comando: Select = (
        select(
            Movimento.id.label("movimento"),
            Movimento.nf_numero,
            Movimento.nf_chave,
            Movimento.tipo,
            Movimento.criado_em,
            Item.id.label("id"),
            Produto.nome.label("nome"),
            Produto.sku.label("sku"),
            Produto.barcode.label("barcode"),
            Produto.ncm.label("ncm"),
            Fornecedor.nome.label("fornecedor"),
            Item.qtd_unidades,
            Item.preco_unit,
            (Item.qtd_unidades * Item.preco_unit).label("subtotal"),
        )
        .join(Item, Movimento.id == Item.movimento_id)
        .join(Produto, Item.produto_id == Produto.id)
        .join(Fornecedor, Produto.fornecedor_id == Fornecedor.id)
        .where(Movimento.nf_chave == nf_chave)
    )

    itens: Sequence[RowMapping] = (
        sessao.execute(statement=comando.order_by(Item.id)).mappings().all()
    )

    memoria: StringIO = StringIO()
    writer = csv.writer(memoria, delimiter=";")

    writer.writerow(
        [
            "movimento",
            "nf_numero",
            "nf_chave",
            "tipo",
            "data",
            "item",
            "nome",
            "sku",
            "barcode",
            "ncm",
            "fornecedor",
            "qtd",
            "preco_unit",
            "subtotal",
        ]
    )

    for item in itens:
        writer.writerow(
            [
                item["movimento"],
                item["nf_numero"],
                item["nf_chave"],
                item["tipo"],
                formatar_data(data=item["criado_em"]),
                item["id"],
                item["nome"],
                item["sku"],
                item["barcode"],
                item["ncm"],
                item["fornecedor"],
                item["qtd_unidades"],
                item["preco_unit"],
                item["subtotal"],
            ]
        )

    return Response(
        content=memoria.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=movimento_{nf_chave}.csv"
        },
    )


@router.get(
    "/{id}/detalhes",
    response_model=MovimentoDetalhesResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca os detalhes de um movimento pelo ID",
)
def buscar_detalhes_movimento_id(id: int, sessao: Sessao) -> Movimento:
    """Busca os detalhes de um movimento pelo ID.

    :param id: ID do movimento a ser consultado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Movimento encontrado com seus itens.
    :rtype: Movimento
    :raises HTTPException: Se o movimento não for encontrado.
    """
    movimento: Movimento | None = sessao.scalar(
        select(Movimento)
        .where(Movimento.id == id)
        .options(selectinload(Movimento.itens))
    )

    if movimento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    return movimento


@router.get(
    "/{id}/detalhes/exportar",
    status_code=status.HTTP_200_OK,
    summary="Exporta um relatório dos itens de um movimento em formato CSV pelo ID",
)
def exportar_relatorio_itens_movimento_id(id: int, sessao: Sessao) -> Response:
    """Exporta um relatório dos itens de um movimento em formato CSV pelo ID.

    :param id: ID do movimento a ser exportado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Resposta HTTP contendo o relatório dos itens do movimento em formato CSV.
    :rtype: Response
    :raises HTTPException: Se o movimento não for encontrado.
    """
    if not sessao.get(Movimento, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    comando: Select = (
        select(
            Movimento.id.label("movimento"),
            Movimento.nf_numero,
            Movimento.nf_chave,
            Movimento.tipo,
            Movimento.criado_em,
            Item.id.label("id"),
            Produto.nome.label("nome"),
            Produto.sku.label("sku"),
            Produto.barcode.label("barcode"),
            Produto.ncm.label("ncm"),
            Fornecedor.nome.label("fornecedor"),
            Item.qtd_unidades,
            Item.preco_unit,
            (Item.qtd_unidades * Item.preco_unit).label("subtotal"),
        )
        .join(Item, Movimento.id == Item.movimento_id)
        .join(Produto, Item.produto_id == Produto.id)
        .join(Fornecedor, Produto.fornecedor_id == Fornecedor.id)
        .where(Movimento.id == id)
    )

    itens: Sequence[RowMapping] = (
        sessao.execute(statement=comando.order_by(Item.id)).mappings().all()
    )

    memoria: StringIO = StringIO()
    writer = csv.writer(memoria, delimiter=";")

    writer.writerow(
        [
            "movimento",
            "nf_numero",
            "nf_chave",
            "tipo",
            "data",
            "item",
            "nome",
            "sku",
            "barcode",
            "ncm",
            "fornecedor",
            "qtd",
            "preco_unit",
            "subtotal",
        ]
    )

    for item in itens:
        writer.writerow(
            [
                item["movimento"],
                item["nf_numero"],
                item["nf_chave"],
                item["tipo"],
                formatar_data(data=item["criado_em"]),
                item["id"],
                item["nome"],
                item["sku"],
                item["barcode"],
                item["ncm"],
                item["fornecedor"],
                item["qtd_unidades"],
                item["preco_unit"],
                item["subtotal"],
            ]
        )

    return Response(
        content=memoria.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=movimento_{id}.csv"},
    )


@router.get(
    "/{id}",
    response_model=MovimentoResumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca o resumo de um movimento pelo ID",
)
def buscar_resumo_movimento_id(id: int, sessao: Sessao) -> Movimento:
    """Busca o resumo de um movimento pelo ID.

    :param id: ID do movimento a ser consultado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Movimento encontrado.
    :rtype: Movimento
    :raises HTTPException: Se o movimento não for encontrado.
    """
    movimento: Movimento | None = sessao.scalar(
        select(Movimento)
        .where(Movimento.id == id)
        .options(selectinload(Movimento.itens))
    )

    if movimento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento não encontrado.",
        )

    return movimento


@router.post(
    "/",
    response_model=MovimentoDetalhesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo movimento",
)
def criar_movimento(movimento: MovimentoCreate, sessao: Sessao) -> Movimento:
    """Cria um novo movimento.

    :param movimento: Dados do movimento a ser criado.
    :type movimento: MovimentoCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Movimento criado com seus itens.
    :rtype: Movimento
    :raises HTTPException: Se o fornecedor não for encontrado.
    :raises HTTPException: Se o fornecedor estiver inativo.
    :raises HTTPException: Se existirem um ou mais produtos não cadastrados.
    :raises HTTPException: Se o estoque for insuficiente para algum produto em um movimento de saída.
    """
    fornecedor: Fornecedor | None = sessao.scalar(
        statement=select(Fornecedor).where(Fornecedor.cnpj == movimento.fornecedor_cnpj)
    )

    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Fornecedor não encontrado.",
        )

    if not fornecedor.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Fornecedor inativo."
        )

    barcodes: set[str] = {item.barcode for item in movimento.itens}

    produtos: Sequence[Produto] = sessao.scalars(
        select(Produto).where(Produto.barcode.in_(barcodes))
    ).all()

    if len(barcodes) != len(produtos):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Não é possível criar o movimento. Existem um ou mais produtos não cadastrados.",
        )

    novo_movimento = Movimento(
        nf_numero=movimento.nf_numero,
        nf_chave=movimento.nf_chave,
        tipo=movimento.tipo,
        fornecedor_id=fornecedor.id,
    )

    sessao.add(novo_movimento)
    sessao.flush()

    mapa_produtos: dict[str, Produto] = {
        produto.barcode: produto for produto in produtos
    }

    for item in movimento.itens:
        produto = mapa_produtos[item.barcode]

        if movimento.tipo == "Entrada":
            produto.estoque_atual += item.qtd_unidades

        elif movimento.tipo == "Saida":
            if produto.estoque_atual < item.qtd_unidades:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Estoque insuficiente para o produto '{produto.nome}'.",
                )

            produto.estoque_atual -= item.qtd_unidades

        novo_item = Item(
            movimento_id=novo_movimento.id,
            produto_id=produto.id,
            qtd_unidades=item.qtd_unidades,
            preco_unit=item.preco_unit,
        )

        sessao.add(novo_item)

    sessao.commit()
    sessao.refresh(novo_movimento)

    return novo_movimento
