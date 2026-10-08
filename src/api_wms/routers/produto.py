"""Rotas responsáveis pelas operações de consulta, gerenciamento e exportação de produtos."""

import csv
import re
from collections.abc import Sequence
from decimal import Decimal
from io import StringIO
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi import status as status_code
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from api_wms.database import iniciar_sessao
from api_wms.filtros.produto import FiltrosProduto
from api_wms.models.endereco import Endereco
from api_wms.models.fornecedor import Fornecedor
from api_wms.models.produto import Produto
from api_wms.models.subcategoria import Subcategoria
from api_wms.models.unidade import Unidade
from api_wms.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from api_wms.utils import formatar_data

router: APIRouter = APIRouter(prefix="/produtos", tags=["Produtos"])
Sessao = Annotated[Session, Depends(dependency=iniciar_sessao)]


def _filtrar_produtos(comando: Select, filtros: FiltrosProduto) -> Select:
    """Aplica os filtros informados à consulta de produtos.

    :param comando: Comando SQL utilizado para consulta dos produtos.
    :type comando: Select
    :param filtros: Filtros utilizados para restringir os produtos consultados.
    :type filtros: FiltrosProduto
    :return: Comando SQL com os filtros aplicados.
    :rtype: Select
    """
    if filtros.nome is not None:
        comando = comando.where(Produto.nome.ilike(f"%{filtros.nome}%"))

    if filtros.sku is not None:
        comando = comando.where(Produto.sku.ilike(f"{filtros.sku}%"))

    if filtros.ncm is not None:
        comando = comando.where(
            Produto.ncm.like(
                f"{re.sub(pattern=r'[^0-9]', repl='', string=filtros.ncm)}%"
            )
        )

    if filtros.fornecedor_id is not None:
        comando = comando.where(Produto.fornecedor_id == filtros.fornecedor_id)

    if filtros.subcategoria_id is not None:
        comando = comando.where(Produto.subcategoria_id == filtros.subcategoria_id)

    if filtros.estoque_atual_min is not None:
        comando = comando.where(Produto.estoque_atual >= filtros.estoque_atual_min)

    if filtros.estoque_atual_max is not None:
        comando = comando.where(Produto.estoque_atual <= filtros.estoque_atual_max)

    if filtros.unidade_id is not None:
        comando = comando.where(Produto.unidade_id == filtros.unidade_id)

    if filtros.status is not None:
        comando = comando.where(Produto.status == filtros.status)

    return comando


@router.get(
    "/",
    response_model=list[ProdutoResponse],
    status_code=status_code.HTTP_200_OK,
    summary="Filtra e lista os produtos",
)
def listar_produtos(
    sessao: Sessao,
    nome: str | None = None,
    sku: str | None = None,
    ncm: str | None = None,
    fornecedor_id: int | None = Query(default=None, alias="fornecedor"),
    subcategoria_id: int | None = Query(default=None, alias="subcategoria"),
    estoque_atual_min: Decimal | None = Query(default=None, alias="qtd_min"),
    estoque_atual_max: Decimal | None = Query(default=None, alias="qtd_max"),
    unidade_id: int | None = Query(default=None, alias="unidade"),
    status: bool | None = None,
    limit: int = Query(
        100, ge=1, le=500, description="Limite de resultados por página"
    ),
    offset: int = Query(0, ge=0, description="Paginação de resultados"),
) -> Sequence[Produto]:
    """Filtra e lista os produtos.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome do produto utilizado como filtro.
    :type nome: str | None
    :param sku: SKU do produto utilizado como filtro.
    :type sku: str | None
    :param ncm: NCM do produto utilizado como filtro.
    :type ncm: str | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    :param subcategoria_id: ID da subcategoria utilizada como filtro.
    :type subcategoria_id: int | None
    :param estoque_atual_min: Quantidade mínima de estoque atual utilizada como filtro.
    :type estoque_atual_min: Decimal | None
    :param estoque_atual_max: Quantidade máxima de estoque atual utilizada como filtro.
    :type estoque_atual_max: Decimal | None
    :param unidade_id: ID da unidade utilizada como filtro.
    :type unidade_id: int | None
    :param status: Status do produto utilizado como filtro.
    :type status: bool | None
    :param limit: Limite de resultados por página.
    :type limit: int
    :param offset: Paginação de resultados.
    :type offset: int
    :return: Sequência de produtos encontrados.
    :rtype: Sequence[Produto]
    """
    filtros: FiltrosProduto = FiltrosProduto(
        nome=nome,
        sku=sku,
        ncm=ncm,
        fornecedor_id=fornecedor_id,
        subcategoria_id=subcategoria_id,
        estoque_atual_min=estoque_atual_min,
        estoque_atual_max=estoque_atual_max,
        unidade_id=unidade_id,
        status=status,
    )
    comando: Select = _filtrar_produtos(comando=select(Produto), filtros=filtros)

    return sessao.scalars(
        statement=comando.order_by(Produto.nome).offset(offset).limit(limit)
    ).all()


@router.get(
    "/exportar",
    status_code=status_code.HTTP_200_OK,
    summary="Exporta um relatório dos produtos em formato CSV",
)
def exportar_relatorio_produtos(
    sessao: Sessao,
    nome: str | None = None,
    sku: str | None = None,
    ncm: str | None = None,
    fornecedor_id: int | None = Query(default=None, alias="fornecedor"),
    subcategoria_id: int | None = Query(default=None, alias="subcategoria"),
    estoque_atual_min: Decimal | None = Query(default=None, alias="qtd_min"),
    estoque_atual_max: Decimal | None = Query(default=None, alias="qtd_max"),
    unidade_id: int | None = Query(default=None, alias="unidade"),
    status: bool | None = None,
) -> Response:
    """Exporta um relatório dos produtos em formato CSV.

    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :param nome: Nome do produto utilizado como filtro.
    :type nome: str | None
    :param sku: SKU do produto utilizado como filtro.
    :type sku: str | None
    :param ncm: NCM do produto utilizado como filtro.
    :type ncm: str | None
    :param fornecedor_id: ID do fornecedor utilizado como filtro.
    :type fornecedor_id: int | None
    :param subcategoria_id: ID da subcategoria utilizada como filtro.
    :type subcategoria_id: int | None
    :param estoque_atual_min: Quantidade mínima de estoque atual utilizada como filtro.
    :type estoque_atual_min: Decimal | None
    :param estoque_atual_max: Quantidade máxima de estoque atual utilizada como filtro.
    :type estoque_atual_max: Decimal | None
    :param unidade_id: ID da unidade utilizada como filtro.
    :type unidade_id: int | None
    :param status: Status do produto utilizado como filtro.
    :type status: bool | None
    :return: Resposta HTTP contendo o relatório dos produtos em formato CSV.
    :rtype: Response
    :raises HTTPException: Se não houver produtos que correspondam aos filtros fornecidos.
    """
    filtros: FiltrosProduto = FiltrosProduto(
        nome=nome,
        sku=sku,
        ncm=ncm,
        fornecedor_id=fornecedor_id,
        subcategoria_id=subcategoria_id,
        estoque_atual_min=estoque_atual_min,
        estoque_atual_max=estoque_atual_max,
        unidade_id=unidade_id,
        status=status,
    )
    comando: Select = _filtrar_produtos(comando=select(Produto), filtros=filtros)

    comando = comando.options(
        joinedload(Produto.endereco),
        joinedload(Produto.fornecedor),
        joinedload(Produto.subcategoria).joinedload(Subcategoria.categoria),
        joinedload(Produto.unidade),
    )

    produtos: Sequence[Produto] = sessao.scalars(
        statement=comando.order_by(Produto.nome)
    ).all()

    if not produtos:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="Não há produtos que correspondam aos filtros fornecidos.",
        )

    memoria: StringIO = StringIO()
    writer = csv.writer(memoria, delimiter=";")

    writer.writerow(
        [
            "id",
            "nome",
            "descrição",
            "sku",
            "barcode",
            "ncm",
            "endereço",
            "fornecedor",
            "categoria",
            "subcategoria",
            "estoque_atual",
            "estoque_min",
            "estoque_max",
            "unidade_nome",
            "unidade_sigla",
            "preco_venda",
            "preco_custo",
            "status",
            "criado",
            "atualizado",
        ]
    )

    for produto in produtos:
        writer.writerow(
            [
                produto.id,
                produto.nome,
                produto.descricao,
                produto.sku,
                produto.barcode,
                produto.ncm,
                produto.endereco.cea,
                produto.fornecedor.nome,
                produto.subcategoria.categoria.nome,
                produto.subcategoria.nome,
                produto.estoque_atual,
                produto.estoque_min,
                produto.estoque_max,
                produto.unidade.nome,
                produto.unidade.sigla,
                produto.preco_venda,
                produto.preco_custo,
                "ativo" if produto.status else "inativo",
                formatar_data(data=produto.criado_em),
                formatar_data(data=produto.atualizado_em),
            ]
        )

    return Response(
        content=memoria.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=produtos.csv"},
    )


@router.get(
    "/sku/{sku}",
    response_model=ProdutoResponse,
    status_code=status_code.HTTP_200_OK,
    summary="Busca um produto pelo código SKU",
)
def buscar_produto_sku(sku: str, sessao: Sessao) -> Produto:
    """Busca um produto pelo código SKU.

    :param sku: Código SKU do produto a ser consultado.
    :type sku: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Produto encontrado.
    :rtype: Produto
    :raises HTTPException: Se o produto não for encontrado.
    """
    produto: Produto | None = sessao.scalar(
        statement=select(Produto).where(Produto.sku == sku.upper())
    )

    if produto is None:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return produto


@router.get(
    "/barcode/{barcode}",
    response_model=ProdutoResponse,
    status_code=status_code.HTTP_200_OK,
    summary="Busca um produto pelo código de barras EAN-13",
)
def buscar_produto_barcode(barcode: str, sessao: Sessao) -> Produto:
    """Busca um produto pelo código de barras EAN-13.

    :param barcode: Código de barras EAN-13 do produto a ser consultado.
    :type barcode: str
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Produto encontrado.
    :rtype: Produto
    :raises HTTPException: Se o produto não for encontrado.
    """
    produto: Produto | None = sessao.scalar(
        statement=select(Produto).where(
            Produto.barcode == re.sub(pattern=r"[^0-9]", repl="", string=barcode)
        )
    )

    if produto is None:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return produto


@router.get(
    "/{id}",
    response_model=ProdutoResponse,
    status_code=status_code.HTTP_200_OK,
    summary="Busca um produto pelo ID",
)
def buscar_produto_id(id: int, sessao: Sessao) -> Produto:
    """Busca um produto pelo ID.

    :param id: ID do produto a ser consultado.
    :type id: int
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Produto encontrado.
    :rtype: Produto
    :raises HTTPException: Se o produto não for encontrado.
    """
    produto: Produto | None = sessao.get(Produto, id)

    if produto is None:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return produto


@router.post(
    "/",
    response_model=ProdutoResponse,
    status_code=status_code.HTTP_201_CREATED,
    summary="Cria um novo produto",
)
def criar_produto(produto: ProdutoCreate, sessao: Sessao) -> Produto:
    """Cria um novo produto.

    :param produto: Dados do produto a ser criado.
    :type produto: ProdutoCreate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Produto criado.
    :rtype: Produto
    :raises HTTPException: Se o fornecedor não for encontrado.
    :raises HTTPException: Se o fornecedor estiver inativo.
    :raises HTTPException: Se a subcategoria de produto não for encontrada.
    :raises HTTPException: Se a subcategoria de produto estiver inativa.
    :raises HTTPException: Se a unidade de medida não for encontrada.
    :raises HTTPException: Se a unidade de medida estiver inativa.
    :raises HTTPException: Se já existir um produto com o mesmo nome.
    :raises HTTPException: Se já existir um produto com o mesmo código SKU.
    :raises HTTPException: Se já existir um produto com o mesmo código de barras EAN-13.
    :raises HTTPException: Se não houver endereço de armazenagem disponível para alocação do produto.
    :raises HTTPException: Se o endereço de armazenagem informado não for encontrado.
    :raises HTTPException: Se o endereço de armazenagem informado estiver indisponível.
    """
    fornecedor: Fornecedor | None = sessao.get(Fornecedor, produto.fornecedor_id)

    if fornecedor is None:
        raise HTTPException(
            status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Fornecedor não encontrado.",
        )

    if not fornecedor.status:
        raise HTTPException(
            status_code=status_code.HTTP_409_CONFLICT, detail="Fornecedor inativo."
        )

    subcategoria: Subcategoria | None = sessao.get(
        Subcategoria, produto.subcategoria_id
    )

    if subcategoria is None:
        raise HTTPException(
            status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Subcategoria de produto não encontrada.",
        )

    if not subcategoria.status:
        raise HTTPException(
            status_code=status_code.HTTP_409_CONFLICT,
            detail="Subcategoria de produto inativa.",
        )

    unidade: Unidade | None = sessao.get(Unidade, produto.unidade_id)

    if unidade is None:
        raise HTTPException(
            status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unidade de medida não encontrada.",
        )

    if not unidade.status:
        raise HTTPException(
            status_code=status_code.HTTP_409_CONFLICT,
            detail="Unidade de medida inativa.",
        )

    resultado: Produto | None = sessao.scalar(
        statement=select(Produto).where(
            (Produto.nome == produto.nome)
            | (Produto.sku == produto.sku)
            | (Produto.barcode == produto.barcode)
        )
    )

    if resultado:
        if resultado.nome == produto.nome:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Já existe um produto cadastrado com este nome.",
            )

        elif resultado.sku == produto.sku:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Já existe um produto cadastrado com este código SKU.",
            )

        elif resultado.barcode == produto.barcode:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Já existe um produto cadastrado com este código de barras EAN-13.",
            )

    dict_novo_produto: dict[str, Any] = produto.model_dump()

    if produto.endereco_id is None:
        endereco: Endereco | None = sessao.scalar(
            statement=select(Endereco).where(Endereco.status).limit(limit=1)
        )

        if endereco is None:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Não há endereço de armazenagem disponível para alocação do produto.",
            )

        dict_novo_produto["endereco_id"] = endereco.id

    else:
        endereco: Endereco | None = sessao.get(Endereco, produto.endereco_id)

        if endereco is None:
            raise HTTPException(
                status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Endereço de armazenagem não encontrado.",
            )

        if not endereco.status:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Já existe um produto alocado neste endereço de armazenagem.",
            )

    endereco.status = False

    novo_produto: Produto = Produto(**dict_novo_produto)

    sessao.add(instance=novo_produto)
    sessao.commit()
    sessao.refresh(instance=novo_produto)

    return novo_produto


@router.patch(
    "/{id}",
    response_model=ProdutoResponse,
    status_code=status_code.HTTP_200_OK,
    summary="Atualiza um produto pelo ID",
)
def atualizar_produto_id(id: int, payload: ProdutoUpdate, sessao: Sessao) -> Produto:
    """Atualiza um produto pelo ID.

    :param id: ID do produto a ser atualizado.
    :type id: int
    :param payload: Dados do produto a serem atualizados.
    :type payload: ProdutoUpdate
    :param sessao: Sessão ativa com o banco de dados.
    :type sessao: Session
    :return: Produto atualizado.
    :rtype: Produto
    :raises HTTPException: Se o produto não for encontrado.
    :raises HTTPException: Se já existir outro produto com o mesmo nome.
    :raises HTTPException: Se a subcategoria de produto não for encontrada.
    :raises HTTPException: Se a subcategoria de produto estiver inativa.
    :raises HTTPException: Se o endereço de armazenagem não for encontrado.
    :raises HTTPException: Se o endereço de armazenagem estiver indisponível.
    """
    produto: Produto | None = sessao.get(Produto, id)

    if not produto:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND, detail="Produto não encontrado."
        )

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    if not update_data:
        return produto

    if "nome" in update_data and sessao.scalar(
        statement=select(Produto).where(
            (Produto.nome == update_data["nome"]) & (Produto.id != id)
        )
    ):
        raise HTTPException(
            status_code=status_code.HTTP_409_CONFLICT,
            detail="Já existe um produto cadastrado com este nome.",
        )

    if "subcategoria_id" in update_data:
        subcategoria: Subcategoria | None = sessao.get(
            Subcategoria, update_data["subcategoria_id"]
        )

        if subcategoria is None:
            raise HTTPException(
                status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Subcategoria de produto não encontrada.",
            )

        if not subcategoria.status:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Subcategoria de produto inativa.",
            )

    if (
        "endereco_id" in update_data
        and update_data["endereco_id"] != produto.endereco_id
    ):
        endereco_update: Endereco | None = sessao.get(
            Endereco, update_data["endereco_id"]
        )

        if endereco_update is None:
            raise HTTPException(
                status_code=status_code.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Endereço de armazenagem não encontrado.",
            )

        if not endereco_update.status:
            raise HTTPException(
                status_code=status_code.HTTP_409_CONFLICT,
                detail="Já existe um produto alocado neste endereço de armazenagem.",
            )

        endereco_update.status = False

        endereco_anterior: Endereco | None = sessao.get(Endereco, produto.endereco_id)
        if endereco_anterior:
            endereco_anterior.status = True

    for atributo, valor in update_data.items():
        setattr(produto, atributo, valor)

    sessao.commit()
    sessao.refresh(produto)

    return produto
