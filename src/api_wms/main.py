"""Ponto de entrada da aplicação FastAPI, responsável pela configuração da API,
inicialização do banco de dados e registro dos routers da aplicação.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api_wms.database import engine
from api_wms.models.base import Base
from api_wms.routers import (
    categoria,
    endereco,
    fornecedor,
    movimento,
    produto,
    subcategoria,
    unidade,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configura o ciclo de vida da aplicação e inicializa o banco de dados.

    :param app: Instância da aplicação FastAPI.
    :type app: FastAPI
    :return: Gerenciador assíncrono do ciclo de vida da aplicação.
    :rtype: AsyncIterator[None]
    """
    if os.getenv("AMBIENTE") != "teste":
        Base.metadata.create_all(bind=engine)

    yield


app: FastAPI = FastAPI(
    title="API WMS",
    description="API REST em Python para gestão de armazéns (WMS) e rastreabilidade de estoques.",
    version="1.0.0",
    contact={
        "name": "André Magalhães",
        "url": "https://github.com/andrellmagalhaes/api-wms",
        "email": "andreluizmagalhaes@hotmail.com",
    },
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False, status_code=200, tags=["Global"])
def index_global() -> dict[str, str | int]:
    """Retorna o status de funcionamento da API.

    :return: Dicionário contendo o status e a mensagem de funcionamento da API.
    :rtype: dict[str, str | int]
    """
    return {"status": 200, "mensagem": "OK"}


@app.get("/v1/", include_in_schema=False, status_code=200, tags=["Index v1"])
@app.get("/v1/index", include_in_schema=False, status_code=200, tags=["Index v1"])
def index_v1() -> dict[str, str | int]:
    """Retorna o status de funcionamento da versão 1.0.0 da API.

    :return: Dicionário contendo o status, a mensagem e a versão da API.
    :rtype: dict[str, str | int]
    """
    return {"status": 200, "mensagem": "API funcionando", "versão": "1.0.0"}


app.include_router(categoria.router, prefix="/v1")
app.include_router(endereco.router, prefix="/v1")
app.include_router(fornecedor.router, prefix="/v1")
app.include_router(movimento.router, prefix="/v1")
app.include_router(produto.router, prefix="/v1")
app.include_router(subcategoria.router, prefix="/v1")
app.include_router(unidade.router, prefix="/v1")
