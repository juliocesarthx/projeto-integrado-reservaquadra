import os
import sqlite3

PASTA_APP = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PADRAO = os.path.join(os.path.dirname(PASTA_APP), "instance", "reservaquadra.db")


def caminho_do_banco():
    return os.environ.get("RESERVAQUADRA_DB", CAMINHO_PADRAO)


def conectar():
    caminho = caminho_do_banco()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    with open(os.path.join(PASTA_APP, "schema.sql"), encoding="utf-8") as arquivo:
        script = arquivo.read()
    with conectar() as conexao:
        conexao.executescript(script)
