"""Testes de integração das rotas da entidade Subcategoria."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_subcategoria_produto_id_200_ok(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/subcategorias/{subcategorias[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Massas"


def test_buscar_subcategoria_produto_id_404_not_found(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/subcategorias/10").status_code == 404


def test_listar_subcategorias_produto_sem_filtros_200_ok(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/subcategorias")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["nome"] == "Carnes"


def test_listar_subcategorias_produto_filtro_unico_200_ok(
    client: TestClient,
    subcategorias: list[dict[str, Any]],
    categorias: list[dict[str, Any]],
) -> None:
    resposta: Any = client.get("/v1/subcategorias?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Carnes"


def test_listar_subcategorias_produto_filtro_duplo_200_ok(
    client: TestClient,
    subcategorias: list[dict[str, Any]],
    categorias: list[dict[str, Any]],
) -> None:
    resposta: Any = client.get(
        f"/v1/subcategorias?categoria={categorias[0]['id']}&status=true"
    )

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Carnes"


def test_listar_subcategorias_produto_sem_resultados_200_ok(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/subcategorias?nome=acess")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_excluir_subcategoria_produto_id_204_no_content(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert (
        client.delete(f"/v1/subcategorias/{subcategorias[0]['id']}").status_code == 204
    )
    assert client.get(f"/v1/subcategorias/{subcategorias[0]['id']}").status_code == 404


def test_excluir_subcategoria_produto_id_409_conflict_dependencia(
    client: TestClient,
    subcategorias: list[dict[str, Any]],
    produtos: list[dict[str, Any]],
) -> None:
    assert (
        client.delete(f"/v1/subcategorias/{subcategorias[0]['id']}").status_code == 409
    )
    assert (
        client.get(f"/v1/subcategorias/{subcategorias[0]['id']}").json()["nome"]
        == "Massas"
    )


def test_excluir_subcategoria_produto_id_404_not_found(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert client.delete("/v1/subcategorias/10").status_code == 404


def test_criar_subcategoria_produto_201_created(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    resposta: Any = client.post(
        "/v1/subcategorias",
        json={"nome": "Massas", "categoria_id": categorias[0]["id"], "status": True},
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Massas"
    assert client.get(f"/v1/subcategorias/{resposta.json()['id']}").status_code == 200


def test_criar_subcategoria_produto_422_unprocessable_content_categoria_produto_inexistente(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/subcategorias",
            json={"nome": "Massas", "categoria_id": 10, "status": True},
        ).status_code
        == 422
    )


def test_criar_subcategoria_produto_409_conflict_categoria_produto_inativa(
    client: TestClient, categorias: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/subcategorias",
            json={
                "nome": "Televisores",
                "categoria_id": categorias[2]["id"],
                "status": True,
            },
        ).status_code
        == 409
    )


def test_criar_subcategoria_produto_409_conflict_duplicidade_nome_categoria_id(
    client: TestClient,
    subcategorias: list[dict[str, Any]],
    categorias: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/subcategorias",
            json={
                "nome": subcategorias[0]["nome"],
                "categoria_id": subcategorias[0]["categoria_id"],
                "status": True,
            },
        ).status_code
        == 409
    )


def test_atualizar_subcategoria_produto_id_200_ok(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/subcategorias/{subcategorias[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/subcategorias/{subcategorias[0]['id']}").json()[
        "status"
    ]


def test_atualizar_subcategoria_produto_id_404_not_found(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert (
        client.patch("/v1/subcategorias/10", json={"status": False}).status_code == 404
    )


def test_atualizar_subcategoria_produto_id_409_conflict_duplicidade_nome_categoria_id(
    client: TestClient, subcategorias: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/subcategorias/{subcategorias[0]['id']}",
            json={"nome": subcategorias[1]["nome"]},
        ).status_code
        == 409
    )
