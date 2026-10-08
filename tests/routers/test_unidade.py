"""Testes de integração das rotas da entidade Unidade."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_unidade_medida_id_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/unidades/{unidades[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Unidade"


def test_buscar_unidade_medida_id_404_not_found(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/unidades/10").status_code == 404


def test_listar_unidades_medida_sem_filtros_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/unidades")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["nome"] == "Metro"


def test_listar_unidades_medida_filtro_unico_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/unidades?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Metro"


def test_listar_unidades_medida_filtro_duplo_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/unidades?nome=metro&status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Metro"


def test_listar_unidades_medida_sem_resultados_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/unidades?nome=tonelada")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_excluir_unidade_medida_id_204_no_content(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert client.delete(f"/v1/unidades/{unidades[0]['id']}").status_code == 204
    assert client.get(f"/v1/unidades/{unidades[0]['id']}").status_code == 404


def test_excluir_unidade_medida_id_409_conflict_dependencia(
    client: TestClient,
    unidades: list[dict[str, Any]],
    produtos: list[dict[str, Any]],
) -> None:
    assert client.delete(f"/v1/unidades/{unidades[0]['id']}").status_code == 409
    assert client.get(f"/v1/unidades/{unidades[0]['id']}").json()["nome"] == "Unidade"


def test_excluir_unidade_medida_id_404_not_found(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert client.delete("/v1/unidades/10").status_code == 404


def test_criar_unidade_medida_201_created(client: TestClient) -> None:
    resposta: Any = client.post(
        "/v1/unidades", json={"nome": "Unidade", "sigla": "UN", "status": True}
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Unidade"
    assert client.get(f"/v1/unidades/{resposta.json()['id']}").status_code == 200


def test_criar_unidade_medida_409_conflict_duplicidade_nome(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/unidades",
            json={"nome": unidades[0]["nome"], "sigla": "AB", "status": True},
        ).status_code
        == 409
    )


def test_criar_unidade_medida_409_conflict_duplicidade_sigla(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/unidades",
            json={"nome": "ABCDEF", "sigla": unidades[0]["sigla"], "status": True},
        ).status_code
        == 409
    )


def test_atualizar_unidade_medida_id_200_ok(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/unidades/{unidades[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/unidades/{unidades[0]['id']}").json()["status"]


def test_atualizar_unidade_medida_id_404_not_found(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert client.patch("/v1/unidades/10", json={"status": False}).status_code == 404


def test_atualizar_unidade_medida_id_409_conflict_duplicidade_nome(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/unidades/{unidades[0]['id']}", json={"nome": unidades[1]["nome"]}
        ).status_code
        == 409
    )


def test_atualizar_unidade_medida_id_409_conflict_duplicidade_sigla(
    client: TestClient, unidades: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/unidades/{unidades[0]['id']}", json={"sigla": unidades[1]["sigla"]}
        ).status_code
        == 409
    )
