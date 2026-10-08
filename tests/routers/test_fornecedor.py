"""Testes de integração das rotas da entidade Fornecedor."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_fornecedor_id_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/fornecedores/{fornecedores[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Comercial Bahia"


def test_buscar_fornecedor_id_404_not_found(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/fornecedores/10").status_code == 404


def test_buscar_fornecedor_cnpj_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/fornecedores/cnpj/98765432000110")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Comercial Bahia"


def test_buscar_fornecedor_cnpj_404_not_found(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/fornecedores/cnpj/12345678901234").status_code == 404


def test_listar_fornecedores_sem_filtros_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/fornecedores")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["nome"] == "Comercial Bahia"


def test_listar_fornecedores_filtro_unico_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/fornecedores?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Comercial Bahia"


def test_listar_fornecedores_filtro_duplo_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/fornecedores?telefone=71&status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Comercial Bahia"


def test_listar_fornecedores_sem_resultados_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/fornecedores?telefone=81")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_excluir_fornecedor_id_204_no_content(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert client.delete(f"/v1/fornecedores/{fornecedores[0]['id']}").status_code == 204
    assert client.get(f"/v1/fornecedores/{fornecedores[0]['id']}").status_code == 404


def test_excluir_fornecedor_id_409_conflict_dependencia(
    client: TestClient,
    fornecedores: list[dict[str, Any]],
    produtos: list[dict[str, Any]],
) -> None:
    assert client.delete(f"/v1/fornecedores/{fornecedores[0]['id']}").status_code == 409
    assert (
        client.get(f"/v1/fornecedores/{fornecedores[0]['id']}").json()["nome"]
        == "Comercial Bahia"
    )


def test_excluir_fornecedor_id_404_not_found(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert client.delete("/v1/fornecedores/10").status_code == 404


def test_criar_fornecedor_201_created(client: TestClient) -> None:
    resposta: Any = client.post(
        "/v1/fornecedores",
        json={
            "nome": "Comercial Bahia",
            "cnpj": "98765432000110",
            "email": "vendas@comercialbahia.com.br",
            "telefone": "7132345678",
            "status": True,
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Comercial Bahia"
    assert client.get(f"/v1/fornecedores/{resposta.json()['id']}").status_code == 200


def test_criar_fornecedor_409_conflict_duplicidade_nome(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/fornecedores",
            json={
                "nome": fornecedores[0]["nome"],
                "cnpj": "12345678901234",
                "email": "vendas@comercialbahia.com.br",
                "telefone": "7132345678",
                "status": True,
            },
        ).status_code
        == 409
    )


def test_criar_fornecedor_409_conflict_duplicidade_cnpj(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/fornecedores",
            json={
                "nome": "ABCDEFGHIJKLMNOPQ",
                "cnpj": fornecedores[0]["cnpj"],
                "email": "vendas@comercialbahia.com.br",
                "telefone": "7132345678",
                "status": True,
            },
        ).status_code
        == 409
    )


def test_atualizar_fornecedor_id_200_ok(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/fornecedores/{fornecedores[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/fornecedores/{fornecedores[0]['id']}").json()["status"]


def test_atualizar_fornecedor_id_404_not_found(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert (
        client.patch("/v1/fornecedores/10", json={"status": False}).status_code == 404
    )


def test_atualizar_fornecedor_id_409_conflict_duplicidade_nome(
    client: TestClient, fornecedores: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/fornecedores/{fornecedores[0]['id']}",
            json={"nome": fornecedores[1]["nome"]},
        ).status_code
        == 409
    )
