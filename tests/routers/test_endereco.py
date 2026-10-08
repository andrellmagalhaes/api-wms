"""Testes de integração das rotas da entidade Endereco."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_endereco_armazenagem_id_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/enderecos/{enderecos[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["cea"] == "0105120301"


def test_buscar_endereco_armazenagem_id_404_not_found(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/enderecos/10").status_code == 404


def test_buscar_endereco_armazenagem_cea_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/enderecos/cea/0105120301")

    assert resposta.status_code == 200
    assert resposta.json()["cea"] == "0105120301"


def test_buscar_endereco_armazenagem_cea_404_not_found(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/enderecos/cea/1234567890").status_code == 404


def test_listar_enderecos_armazenagem_sem_filtros_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/enderecos")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 4
    assert resposta.json()[0]["cea"] == "0105120301"


def test_listar_enderecos_armazenagem_filtro_unico_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/enderecos?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["cea"] == "0105120301"


def test_listar_enderecos_armazenagem_filtro_duplo_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/enderecos?cea=0105&status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["cea"] == "0105120301"


def test_listar_enderecos_armazenagem_sem_resultados_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/enderecos?cea=02")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_excluir_endereco_armazenagem_id_204_no_content(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert client.delete(f"/v1/enderecos/{enderecos[0]['id']}").status_code == 204
    assert client.get(f"/v1/enderecos/{enderecos[0]['id']}").status_code == 404


def test_excluir_endereco_armazenagem_id_409_conflict_dependencia(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    produtos: list[dict[str, Any]],
) -> None:
    assert client.delete(f"/v1/enderecos/{enderecos[0]['id']}").status_code == 409
    assert (
        client.get(f"/v1/enderecos/{enderecos[0]['id']}").json()["cea"] == "0105120301"
    )


def test_excluir_endereco_armazenagem_id_404_not_found(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert client.delete("/v1/enderecos/10").status_code == 404


def test_criar_endereco_armazenagem_201_created(client: TestClient) -> None:
    resposta: Any = client.post(
        "/v1/enderecos", json={"cea": "0105120301", "status": True}
    )

    assert resposta.status_code == 201
    assert resposta.json()["cea"] == "0105120301"
    assert client.get(f"/v1/enderecos/{resposta.json()['id']}").status_code == 200


def test_criar_endereco_armazenagem_409_conflict_duplicidade_cea(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert (
        client.post(
            "/v1/enderecos", json={"cea": enderecos[0]["cea"], "status": True}
        ).status_code
        == 409
    )


def test_atualizar_endereco_armazenagem_id_200_ok(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/enderecos/{enderecos[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/enderecos/{enderecos[0]['id']}").json()["status"]


def test_atualizar_endereco_armazenagem_id_404_not_found(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert client.patch("/v1/enderecos/10", json={"status": False}).status_code == 404


def test_atualizar_endereco_armazenagem_id_409_conflict_duplicidade_cea(
    client: TestClient, enderecos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/enderecos/{enderecos[0]['id']}",
            json={"cea": enderecos[1]["cea"]},
        ).status_code
        == 409
    )
