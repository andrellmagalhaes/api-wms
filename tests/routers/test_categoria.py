"""Testes de integração das rotas da entidade Categoria."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_categoria_produto_id_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/categorias/{categorias[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Alimentação"


def test_buscar_categoria_produto_id_404_not_found(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/categorias/10").status_code == 404


def test_listar_categorias_produto_sem_filtros_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/categorias")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["nome"] == "Alimentação"


def test_listar_categorias_produto_filtro_unico_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/categorias?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Alimentação"


def test_listar_categorias_produto_filtro_duplo_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/categorias?nome=alimen&status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Alimentação"


def test_listar_categorias_produto_sem_resultados_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/categorias?nome=autom")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_excluir_categoria_produto_id_204_no_content(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert client.delete(f"/v1/categorias/{categorias[0]['id']}").status_code == 204
    assert client.get(f"/v1/categorias/{categorias[0]['id']}").status_code == 404


def test_excluir_categoria_produto_id_409_conflict_dependencia(
    client: TestClient,
    categorias: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
) -> None:
    assert client.delete(f"/v1/categorias/{categorias[0]['id']}").status_code == 409
    assert (
        client.get(f"/v1/categorias/{categorias[0]['id']}").json()["nome"]
        == "Alimentação"
    )


def test_excluir_categoria_produto_id_404_not_found(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert client.delete("/v1/categorias/10").status_code == 404


def test_criar_categoria_produto_201_created(client: TestClient) -> None:
    resposta: Any = client.post(
        "/v1/categorias", json={"nome": "Alimentação", "status": True}
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Alimentação"
    assert client.get(f"/v1/categorias/{resposta.json()['id']}").status_code == 200


def test_criar_categoria_produto_409_conflict_duplicidade_nome(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/categorias", json={"nome": categorias[0]["nome"], "status": True}
        ).status_code
        == 409
    )


def test_atualizar_categoria_produto_id_200_ok(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/categorias/{categorias[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/categorias/{categorias[0]['id']}").json()["status"]


def test_atualizar_categoria_produto_id_404_not_found(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert client.patch("/v1/categorias/10", json={"status": False}).status_code == 404


def test_atualizar_categoria_produto_id_409_conflict_duplicidade_nome(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/categorias/{categorias[0]['id']}",
            json={"nome": categorias[1]["nome"]},
        ).status_code
        == 409
    )
