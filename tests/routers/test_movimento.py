"""Testes de integração das rotas da entidade Movimento."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_resumo_movimento_id_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/movimentos/{movimentos[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nf_numero"] == "100001"


def test_buscar_resumo_movimento_id_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/movimentos/10").status_code == 404


def test_buscar_detalhes_movimento_id_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/movimentos/{movimentos[0]['id']}/detalhes")

    assert resposta.status_code == 200
    assert resposta.json()["nf_numero"] == "100001"


def test_buscar_detalhes_movimento_id_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/movimentos/10/detalhes").status_code == 404


def test_buscar_resumo_movimento_nf_chave_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/movimentos/chave/{movimentos[0]['nf_chave']}")

    assert resposta.status_code == 200
    assert resposta.json()["nf_numero"] == "100001"


def test_buscar_resumo_movimento_nf_chave_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert (
        client.get(
            "/v1/movimentos/chave/12345678901234567890123456789012345678901234"
        ).status_code
        == 404
    )


def test_buscar_detalhes_movimento_nf_chave_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(
        f"/v1/movimentos/chave/{movimentos[0]['nf_chave']}/detalhes"
    )

    assert resposta.status_code == 200
    assert resposta.json()["nf_numero"] == "100001"


def test_buscar_detalhes_movimento_nf_chave_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert (
        client.get(
            "/v1/movimentos/chave/12345678901234567890123456789012345678901234/detalhes"
        ).status_code
        == 404
    )


def test_listar_movimentos_sem_filtros_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/movimentos")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nf_numero"] == "100001"


def test_listar_movimentos_filtro_unico_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/movimentos?tipo=entrada")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nf_numero"] == "100001"


def test_listar_movimentos_filtro_duplo_200_ok(
    client: TestClient,
    movimentos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> None:
    resposta: Any = client.get(
        f"/v1/movimentos?tipo=entrada&fornecedor={fornecedores[0]['id']}"
    )

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nf_numero"] == "100001"


def test_listar_movimentos_sem_resultados_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/movimentos?fornecedor=10")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_criar_movimento_201_created(
    client: TestClient,
    produtos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> None:
    resposta: Any = client.post(
        "/v1/movimentos",
        json={
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
    )

    assert resposta.status_code == 201
    assert resposta.json()["nf_numero"] == "100001"
    assert client.get(f"/v1/movimentos/{resposta.json()['id']}").status_code == 200


def test_criar_movimento_422_unprocessable_content_fornecedor_inexistente(
    client: TestClient,
    produtos: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/movimentos",
            json={
                "nf_numero": "100001",
                "nf_chave": "35261012345678000195550010000010011000000001",
                "tipo": "Entrada",
                "fornecedor_cnpj": "12345678901234",
                "itens": [
                    {
                        "barcode": f"{produtos[0]['barcode']}",
                        "qtd_unidades": 100,
                        "preco_unit": 4.2,
                    },
                ],
            },
        ).status_code
        == 422
    )


def test_criar_movimento_409_conflict_fornecedor_inativo(
    client: TestClient,
    produtos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/movimentos",
            json={
                "nf_numero": "100001",
                "nf_chave": "35261012345678000195550010000010011000000001",
                "tipo": "Entrada",
                "fornecedor_cnpj": f"{fornecedores[2]['cnpj']}",
                "itens": [
                    {
                        "barcode": f"{produtos[0]['barcode']}",
                        "qtd_unidades": 100,
                        "preco_unit": 4.2,
                    },
                ],
            },
        ).status_code
        == 409
    )


def test_criar_movimento_422_unprocessable_content_produto_inexistente(
    client: TestClient,
    fornecedores: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/movimentos",
            json={
                "nf_numero": "100001",
                "nf_chave": "35261012345678000195550010000010011000000001",
                "tipo": "Entrada",
                "fornecedor_cnpj": f"{fornecedores[0]['cnpj']}",
                "itens": [
                    {
                        "barcode": "1234567890123",
                        "qtd_unidades": 100,
                        "preco_unit": 4.2,
                    },
                ],
            },
        ).status_code
        == 422
    )


def test_criar_movimento_409_conflict_produto_estoque_insuficiente(
    client: TestClient,
    produtos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/movimentos",
            json={
                "nf_numero": "100001",
                "nf_chave": "35261012345678000195550010000010011000000001",
                "tipo": "Saida",
                "fornecedor_cnpj": f"{fornecedores[0]['cnpj']}",
                "itens": [
                    {
                        "barcode": f"{produtos[0]['barcode']}",
                        "qtd_unidades": 125.00,
                        "preco_unit": 4.2,
                    },
                ],
            },
        ).status_code
        == 409
    )


def test_exportar_relatorio_movimentos_sem_filtros_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/movimentos/exportar")

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "id;nf_numero;nf_chave;tipo;data;fornecedor;qtd_itens;qtd_unidades;valor_total"
        in resposta.text
    )
    for movimento in movimentos:
        assert movimento["nf_numero"] in resposta.text


def test_exportar_relatorio_movimentos_com_filtro_200_ok(
    client: TestClient,
    movimentos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
) -> None:
    resposta: Any = client.get(
        f"/v1/movimentos/exportar?fornecedor={fornecedores[0]['id']}"
    )

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "id;nf_numero;nf_chave;tipo;data;fornecedor;qtd_itens;qtd_unidades;valor_total"
        in resposta.text
    )
    for movimento in movimentos:
        if movimento["fornecedor_id"] == fornecedores[0]["id"]:
            assert movimento["nf_numero"] in resposta.text

        else:
            assert movimento["nf_numero"] not in resposta.text


def test_exportar_relatorio_movimentos_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/movimentos/exportar?fornecedor=10").status_code == 404


def test_exportar_relatorio_itens_movimento_id_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(
        f"/v1/movimentos/{movimentos[0]['id']}/detalhes/exportar"
    )

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "nf_numero;nf_chave;tipo;data;item;nome;sku;barcode;ncm;fornecedor;qtd;preco_unit;subtotal"
        in resposta.text
    )
    for item in movimentos[0]["itens"]:
        assert item["produto"]["barcode"] in resposta.text


def test_exportar_relatorio_itens_movimento_id_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/movimentos/10/detalhes/exportar").status_code == 404


def test_exportar_relatorio_itens_movimento_nf_chave_200_ok(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(
        f"/v1/movimentos/chave/{movimentos[0]['nf_chave']}/detalhes/exportar"
    )

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "nf_numero;nf_chave;tipo;data;item;nome;sku;barcode;ncm;fornecedor;qtd;preco_unit;subtotal"
        in resposta.text
    )
    for item in movimentos[0]["itens"]:
        assert item["produto"]["barcode"] in resposta.text


def test_exportar_relatorio_itens_movimento_nf_chave_404_not_found(
    client: TestClient, movimentos: list[dict[str, Any]]
) -> None:
    assert (
        client.get(
            "/v1/movimentos/chave/12345678901234567890123456789012345678901234/detalhes/exportar"
        ).status_code
        == 404
    )
