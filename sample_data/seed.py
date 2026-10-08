import json
from pathlib import Path

import requests

BASE_URL: str = "http://127.0.0.1:8000/v1"


def popular_tabela(tabela: str):
    with open(
        file=Path(__file__).parent / f"{tabela}.json", mode="r", encoding="UTF-8"
    ) as stream:
        dados = json.load(fp=stream)

        print(f"Populando a tabela '{tabela}'...")

        for i, item in enumerate(dados, 1):
            if requests.post(url=f"{BASE_URL}/{tabela}", json=item).status_code == 201:
                print(f"registro {i} adicionado com sucesso")

            else:
                print(f"registro {i} ignorado (duplicado)")

        print("")


def executar_seed():
    print("Iniciando o seed...\n")

    for tabela in [
        "unidades",
        "categorias",
        "subcategorias",
        "enderecos",
        "fornecedores",
        "produtos",
        "movimentos",
    ]:
        popular_tabela(tabela=tabela)

    print("Seed finalizado!")


if __name__ == "__main__":
    executar_seed()
