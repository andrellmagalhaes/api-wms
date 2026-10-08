"""Configurações globais e fixtures compartilhadas para o pytest."""

import os
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["AMBIENTE"] = "teste"

from api_wms.database import iniciar_sessao
from api_wms.main import app
from api_wms.models.base import Base

engine: Engine = create_engine(
    url="sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    Base.metadata.create_all(bind=engine)

    def iniciar_sessao_teste() -> Generator[Session, None, None]:
        sessao: Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()

        try:
            yield sessao

        finally:
            sessao.close()

    app.dependency_overrides[iniciar_sessao] = iniciar_sessao_teste

    with TestClient(app) as cliente:
        yield cliente

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def categorias(client: TestClient) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {"nome": "Alimentação", "status": True},
        {"nome": "Bebidas", "status": True},
        {"nome": "Eletrônicos", "status": False},
    ]

    return [
        client.post("/v1/categorias", json=registro).json() for registro in registros
    ]


@pytest.fixture
def enderecos(client: TestClient) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {"cea": "0105120301", "status": True},
        {"cea": "0105120302", "status": True},
        {"cea": "0105120401", "status": True},
        {"cea": "0105120402", "status": False},
    ]

    return [
        client.post("/v1/enderecos", json=registro).json() for registro in registros
    ]


@pytest.fixture
def fornecedores(client: TestClient) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {
            "nome": "Comercial Bahia",
            "cnpj": "98765432000110",
            "email": "vendas@comercialbahia.com.br",
            "telefone": "7132345678",
            "status": True,
        },
        {
            "nome": "Distribuidora Nordeste",
            "cnpj": "12345678000195",
            "email": "contato@distribuidoranordeste.com.br",
            "telefone": "71987654321",
            "status": True,
        },
        {
            "nome": "Fornecedor Central",
            "cnpj": "45678912000134",
            "email": "contato@fornecedorcentral.com",
            "telefone": "11987654321",
            "status": False,
        },
    ]

    return [
        client.post("/v1/fornecedores", json=registro).json() for registro in registros
    ]


@pytest.fixture
def movimentos(
    client: TestClient,
    produtos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {
            "nf_numero": "100001",
            "nf_chave": "35261012345678000195550010000010011000000001",
            "tipo": "Entrada",
            "fornecedor_cnpj": f"{fornecedores[0]['cnpj']}",
            "itens": [
                {
                    "barcode": f"{produtos[0]['barcode']}",
                    "qtd_unidades": 100,
                    "preco_unit": 4.2,
                },
            ],
        },
        {
            "nf_numero": "200001",
            "nf_chave": "35261024681357000186550010000020011000000004",
            "tipo": "Saida",
            "fornecedor_cnpj": f"{fornecedores[1]['cnpj']}",
            "itens": [
                {
                    "barcode": f"{produtos[1]['barcode']}",
                    "qtd_unidades": 20,
                    "preco_unit": 9.5,
                },
            ],
        },
    ]

    return [
        client.post("/v1/movimentos", json=registro).json() for registro in registros
    ]


@pytest.fixture
def produtos(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {
            "nome": "Macarrão Espaguete",
            "descricao": "Macarrão espaguete tradicional de trigo",
            "sku": "MAC-ESP-500G",
            "barcode": "7891000000001",
            "ncm": "19021900",
            "endereco_id": enderecos[0]["id"],
            "fornecedor_id": fornecedores[0]["id"],
            "subcategoria_id": subcategorias[0]["id"],
            "estoque_atual": 120.00,
            "estoque_min": 30.00,
            "estoque_max": 200.00,
            "unidade_id": unidades[0]["id"],
            "preco_venda": 6.90,
            "preco_custo": 4.20,
            "status": True,
        },
        {
            "nome": "Carne Bovina Acém",
            "descricao": "Carne bovina resfriada corte acém",
            "sku": "CAR-ACM-KG",
            "barcode": "7891000000002",
            "ncm": "02013000",
            "endereco_id": enderecos[1]["id"],
            "fornecedor_id": fornecedores[0]["id"],
            "subcategoria_id": subcategorias[1]["id"],
            "estoque_atual": 85.00,
            "estoque_min": 20.00,
            "estoque_max": 120.00,
            "unidade_id": unidades[0]["id"],
            "preco_venda": 32.90,
            "preco_custo": 24.50,
            "status": True,
        },
        {
            "nome": "Carne Bovina de Primeira",
            "descricao": "Carne bovina de primeira qualidade, fresca e resfriada",
            "sku": "CAR-BOV-1KG",
            "barcode": "7891000000003",
            "ncm": "04012010",
            "endereco_id": enderecos[2]["id"],
            "fornecedor_id": fornecedores[1]["id"],
            "subcategoria_id": subcategorias[1]["id"],
            "estoque_atual": 150.00,
            "estoque_min": 40.00,
            "estoque_max": 250.00,
            "unidade_id": unidades[0]["id"],
            "preco_venda": 5.99,
            "preco_custo": 4.10,
            "status": False,
        },
    ]

    return [client.post("/v1/produtos", json=registro).json() for registro in registros]


@pytest.fixture
def subcategorias(
    client: TestClient, categorias: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {"nome": "Massas", "categoria_id": categorias[0]["id"], "status": True},
        {"nome": "Carnes", "categoria_id": categorias[0]["id"], "status": True},
        {"nome": "Refrigerantes", "categoria_id": categorias[1]["id"], "status": False},
    ]

    return [
        client.post("/v1/subcategorias", json=registro).json() for registro in registros
    ]


@pytest.fixture
def unidades(client: TestClient) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = [
        {"nome": "Unidade", "sigla": "UN", "status": True},
        {"nome": "Metro", "sigla": "M", "status": True},
        {"nome": "Quilograma", "sigla": "KG", "status": False},
    ]

    return [client.post("/v1/unidades", json=registro).json() for registro in registros]
