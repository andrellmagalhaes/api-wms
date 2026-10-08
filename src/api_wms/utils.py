"""Funções utilitárias para formatação de dados utilizados pela aplicação."""

from datetime import datetime


def formatar_cnpj(cnpj: str) -> str:
    """Formata um CNPJ para o padrão utilizado na apresentação dos dados.

    :param cnpj: CNPJ a ser formatado.
    :type cnpj: str
    :return: CNPJ formatado no padrão XX.XXX.XXX/XXXX-XX.
    :rtype: str
    """
    return (
        cnpj[:2]
        + "."
        + cnpj[2:5]
        + "."
        + cnpj[5:8]
        + "/"
        + cnpj[8:12]
        + "-"
        + cnpj[12:]
    )


def formatar_data(data: datetime) -> str:
    """Formata uma data e hora para o padrão utilizado na apresentação dos dados.

    :param data: Data e hora a serem formatadas.
    :type data: datetime
    :return: Data e hora formatadas no padrão DD/MM/AAAA HH:MM.
    :rtype: str
    """
    return data.strftime(format="%d/%m/%Y %H:%M")


def formatar_telefone(telefone: str) -> str:
    """Formata um número de telefone para o padrão utilizado na apresentação dos dados.

    :param telefone: Número de telefone a ser formatado.
    :type telefone: str
    :return: Número de telefone formatado conforme a quantidade de dígitos.
    :rtype: str
    """
    if len(telefone) == 10:
        return "(" + telefone[:2] + ")" + " " + telefone[2:6] + "-" + telefone[6:]

    return "(" + telefone[:2] + ")" + " " + telefone[2:7] + "-" + telefone[7:]
