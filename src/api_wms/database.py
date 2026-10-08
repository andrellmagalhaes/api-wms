"""Configuração do banco de dados e gerenciamento de sessões SQLAlchemy."""

from collections.abc import Generator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class Settings(BaseSettings):
    """Configurações utilizadas para conexão com o banco de dados.

    :param DATABASE_URL: URL de conexão com o banco de dados.
    :type DATABASE_URL: str
    """

    DATABASE_URL: str = "sqlite:///database.db"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings: Settings = Settings()

engine: Engine = create_engine(
    url=settings.DATABASE_URL, connect_args={"check_same_thread": False}
)


def iniciar_sessao() -> Generator[Session, None, None]:
    """Inicia uma sessão com o banco de dados e garante seu encerramento.

    :return: Gerador que fornece uma sessão ativa com o banco de dados.
    :rtype: Generator[Session, None, None]
    """
    Sessao: Session = sessionmaker(bind=engine, autoflush=False)()

    try:
        yield Sessao

    finally:
        Sessao.close()
