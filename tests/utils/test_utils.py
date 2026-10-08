"""Testes das funções utilitárias do módulo utils.py."""

from datetime import datetime

from api_wms.utils import formatar_cnpj, formatar_data, formatar_telefone


def test_formatar_cnpj_numerico() -> None:
    assert formatar_cnpj(cnpj="12345678901234") == "12.345.678/9012-34"


def test_formatar_cnpj_alfanumerico() -> None:
    assert formatar_cnpj(cnpj="123ABC456DEF78") == "12.3AB.C45/6DEF-78"


def test_formatar_data() -> None:
    data: datetime = datetime(2026, 10, 6, 12, 30)

    assert formatar_data(data=data) == "06/10/2026 12:30"


def test_formatar_telefone_fixo() -> None:
    assert formatar_telefone(telefone="1234567890") == "(12) 3456-7890"


def test_formatar_telefone_celular() -> None:
    assert formatar_telefone(telefone="12345678901") == "(12) 34567-8901"
