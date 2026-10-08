"""Testes de integração das rotas da entidade Produto."""

from typing import Any

from fastapi.testclient import TestClient


def test_buscar_produto_id_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/produtos/{produtos[0]['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Macarrão Espaguete"


def test_buscar_produto_id_404_not_found(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/produtos/10").status_code == 404


def test_buscar_produto_barcode_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/produtos/barcode/{produtos[0]['barcode']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Macarrão Espaguete"


def test_buscar_produto_barcode_404_not_found(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/produtos/barcode/1234567890123").status_code == 404


def test_buscar_produto_sku_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get(f"/v1/produtos/sku/{produtos[0]['sku']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Macarrão Espaguete"


def test_buscar_produto_sku_404_not_found(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/produtos/sku/ABC-DEF-GHIJ").status_code == 404


def test_listar_produtos_sem_filtros_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 3
    assert resposta.json()[0]["nome"] == "Carne Bovina Acém"


def test_listar_produtos_filtro_unico_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos?status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["nome"] == "Carne Bovina Acém"


def test_listar_produtos_filtro_duplo_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos?sku=car&status=true")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Carne Bovina Acém"


def test_listar_produtos_sem_resultados_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos?sku=bis")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
    assert len(resposta.json()) == 0


def test_criar_produto_201_created(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    resposta: Any = client.post(
        "/v1/produtos",
        json={
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
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Macarrão Espaguete"
    assert client.get(f"/v1/produtos/{resposta.json()['id']}").status_code == 200


def test_criar_produto_422_unprocessable_content_fornecedor_inexistente(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": enderecos[0]["id"],
                "fornecedor_id": 10,
                "subcategoria_id": subcategorias[0]["id"],
                "estoque_atual": 120.00,
                "estoque_min": 30.00,
                "estoque_max": 200.00,
                "unidade_id": unidades[0]["id"],
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 422
    )


def test_criar_produto_409_conflict_fornecedor_inativo(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": enderecos[0]["id"],
                "fornecedor_id": fornecedores[2]["id"],
                "subcategoria_id": subcategorias[0]["id"],
                "estoque_atual": 120.00,
                "estoque_min": 30.00,
                "estoque_max": 200.00,
                "unidade_id": unidades[0]["id"],
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 409
    )


def test_criar_produto_422_unprocessable_content_subcategoria_produto_inexistente(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": enderecos[0]["id"],
                "fornecedor_id": fornecedores[0]["id"],
                "subcategoria_id": 10,
                "estoque_atual": 120.00,
                "estoque_min": 30.00,
                "estoque_max": 200.00,
                "unidade_id": unidades[0]["id"],
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 422
    )


def test_criar_produto_409_conflict_subcategoria_produto_inativa(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": enderecos[0]["id"],
                "fornecedor_id": fornecedores[0]["id"],
                "subcategoria_id": subcategorias[2]["id"],
                "estoque_atual": 120.00,
                "estoque_min": 30.00,
                "estoque_max": 200.00,
                "unidade_id": unidades[0]["id"],
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 409
    )


def test_criar_produto_422_unprocessable_content_unidade_medida_inexistente(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
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
                "unidade_id": 10,
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 422
    )


def test_criar_produto_409_conflict_unidade_medida_inativa(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
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
                "unidade_id": unidades[2]["id"],
                "preco_venda": 6.90,
                "preco_custo": 4.20,
                "status": True,
            },
        ).status_code
        == 409
    )


def test_criar_produto_409_conflict_duplicidade_nome(
    client: TestClient,
    produtos: list[dict[str, Any]],
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": produtos[0]["nome"],
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
        ).status_code
        == 409
    )


def test_criar_produto_409_conflict_duplicidade_sku(
    client: TestClient,
    produtos: list[dict[str, Any]],
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "ABCDEFGHIJKLMNOPQ",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": produtos[0]["sku"],
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
        ).status_code
        == 409
    )


def test_criar_produto_409_conflict_duplicidade_barcode(
    client: TestClient,
    produtos: list[dict[str, Any]],
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "ABCDEFGHIJKLMNOPQ",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "ABC-DEF-GHIJ",
                "barcode": produtos[0]["barcode"],
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
        ).status_code
        == 409
    )


def test_criar_produto_409_conflict_enderecos_armazenagem_indisponiveis(
    client: TestClient,
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    client.post("/v1/enderecos", json={"cea": "0105120301", "status": False})

    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
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
        ).status_code
        == 409
    )


def test_criar_produto_422_unprocessable_content_endereco_armazenagem_inexistente(
    client: TestClient,
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": 10,
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
        ).status_code
        == 422
    )


def test_criar_produto_409_conflict_endereco_armazenagem_indisponivel(
    client: TestClient,
    enderecos: list[dict[str, Any]],
    fornecedores: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
    unidades: list[dict[str, Any]],
) -> None:
    assert (
        client.post(
            "/v1/produtos",
            json={
                "nome": "Macarrão Espaguete",
                "descricao": "Macarrão espaguete tradicional de trigo",
                "sku": "MAC-ESP-500G",
                "barcode": "7891000000001",
                "ncm": "19021900",
                "endereco_id": enderecos[3]["id"],
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
        ).status_code
        == 409
    )


def test_atualizar_produto_id_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}", json={"status": False}
        ).status_code
        == 200
    )
    assert not client.get(f"/v1/produtos/{produtos[0]['id']}").json()["status"]


def test_atualizar_produto_id_404_not_found(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert client.patch("/v1/produtos/10", json={"status": False}).status_code == 404


def test_atualizar_produto_id_409_conflict_duplicidade_nome(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}",
            json={"nome": produtos[1]["nome"]},
        ).status_code
        == 409
    )


def test_atualizar_produto_id_422_unprocessable_content_subcategoria_produto_inexistente(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}",
            json={"subcategoria_id": 10},
        ).status_code
        == 422
    )


def test_atualizar_produto_id_409_conflict_subcategoria_produto_inativa(
    client: TestClient,
    produtos: list[dict[str, Any]],
    subcategorias: list[dict[str, Any]],
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}",
            json={"subcategoria_id": subcategorias[2]["id"]},
        ).status_code
        == 409
    )


def test_atualizar_produto_id_422_unprocessable_content_endereco_armazenagem_inexistente(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}",
            json={"endereco_id": 10},
        ).status_code
        == 422
    )


def test_atualizar_produto_id_409_conflict_endereco_armazenagem_indisponivel(
    client: TestClient,
    produtos: list[dict[str, Any]],
    enderecos: list[dict[str, Any]],
) -> None:
    assert (
        client.patch(
            f"/v1/produtos/{produtos[0]['id']}",
            json={"endereco_id": enderecos[3]["id"]},
        ).status_code
        == 409
    )


def test_exportar_relatorio_produtos_sem_filtros_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos/exportar")

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "id;nome;descrição;sku;barcode;ncm;endereço;fornecedor;categoria;subcategoria;estoque_atual;estoque_min;estoque_max;unidade_nome;unidade_sigla;preco_venda;preco_custo;status;criado;atualizado"
        in resposta.text
    )
    for produto in produtos:
        assert produto["nome"] in resposta.text


def test_exportar_relatorio_produtos_com_filtro_200_ok(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    resposta: Any = client.get("/v1/produtos/exportar?status=true")

    assert resposta.status_code == 200
    assert "text/csv" in resposta.headers["content-type"]
    assert "attachment; filename" in resposta.headers["content-disposition"]
    assert (
        "id;nome;descrição;sku;barcode;ncm;endereço;fornecedor;categoria;subcategoria;estoque_atual;estoque_min;estoque_max;unidade_nome;unidade_sigla;preco_venda;preco_custo;status;criado;atualizado"
        in resposta.text
    )
    for produto in produtos:
        if produto["status"]:
            assert produto["nome"] in resposta.text

        else:
            assert produto["nome"] not in resposta.text


def test_exportar_relatorio_produtos_404_not_found(
    client: TestClient, produtos: list[dict[str, Any]]
) -> None:
    assert client.get("/v1/produtos/exportar?fornecedor=10").status_code == 404
