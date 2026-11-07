import sqlite3
from datetime import date, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from db import conectar

VINCULOS = {"aluno": "Aluno", "professor": "Professor", "colaborador": "Colaborador"}
FINALIDADES = {"aula": "Aula", "treino": "Treino", "evento": "Evento", "lazer": "Uso recreativo"}


class ErroDeValidacao(Exception):
    pass


class Usuario:
    @staticmethod
    def criar(nome, login, senha, perfil):
        with conectar() as con:
            con.execute(
                "INSERT INTO usuario (nome, login, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                (nome, login, generate_password_hash(senha), perfil),
            )

    @staticmethod
    def autenticar(login, senha):
        with conectar() as con:
            linha = con.execute("SELECT * FROM usuario WHERE login = ?", (login.strip(),)).fetchone()
        if linha and check_password_hash(linha["senha_hash"], senha):
            return linha
        return None


class Solicitante:
    @staticmethod
    def cadastrar(nome, vinculo, identificacao, telefone, email=""):
        nome = (nome or "").strip()
        identificacao = (identificacao or "").strip()
        email = (email or "").strip()
        digitos = "".join(c for c in (telefone or "") if c.isdigit())

        if not nome:
            raise ErroDeValidacao("Informe o nome do solicitante.")
        if vinculo not in VINCULOS:
            raise ErroDeValidacao("Escolha o vínculo: aluno, professor ou colaborador.")
        if not identificacao:
            raise ErroDeValidacao("Informe a matrícula, RA ou crachá.")
        if len(digitos) not in (10, 11):
            raise ErroDeValidacao("Telefone inválido: informe DDD + número (10 ou 11 dígitos).")
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            raise ErroDeValidacao("E-mail inválido.")

        with conectar() as con:
            cursor = con.execute(
                """INSERT INTO solicitante (nome, vinculo, identificacao, telefone, email)
                   VALUES (?, ?, ?, ?, ?)""",
                (nome, vinculo, identificacao, digitos, email or None),
            )
            return cursor.lastrowid

    @staticmethod
    def listar():
        with conectar() as con:
            return con.execute("SELECT * FROM solicitante ORDER BY nome").fetchall()


class Quadra:
    @staticmethod
    def cadastrar(nome, modalidade, local=""):
        nome = (nome or "").strip()
        modalidade = (modalidade or "").strip()
        local = (local or "").strip()
        if not nome or not modalidade:
            raise ErroDeValidacao("Informe o nome e a modalidade da quadra.")

        with conectar() as con:
            try:
                cursor = con.execute(
                    "INSERT INTO quadra (nome, modalidade, local) VALUES (?, ?, ?)",
                    (nome, modalidade, local or None),
                )
            except sqlite3.IntegrityError:
                raise ErroDeValidacao("Já existe uma quadra com esse nome.")
            return cursor.lastrowid

    @staticmethod
    def listar_ativas():
        with conectar() as con:
            return con.execute("SELECT * FROM quadra WHERE ativa = 1 ORDER BY nome").fetchall()


class Reserva:
    @staticmethod
    def verificar_conflito(quadra_id, data, hora_inicio, hora_fim):
        with conectar() as con:
            linha = con.execute(
                """SELECT 1 FROM reserva
                    WHERE quadra_id = ? AND data = ? AND status = 'ativa'
                      AND hora_inicio < ? AND hora_fim > ?""",
                (quadra_id, data, hora_fim, hora_inicio),
            ).fetchone()
        return linha is not None

    @staticmethod
    def registrar(solicitante_id, quadra_id, usuario_id, data, hora_inicio, hora_fim, finalidade):
        try:
            date.fromisoformat(data)
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fim = datetime.strptime(hora_fim, "%H:%M")
        except (TypeError, ValueError):
            raise ErroDeValidacao("Informe data e horários válidos.")

        if fim <= inicio:
            raise ErroDeValidacao("O horário de fim deve ser depois do horário de início.")
        if finalidade not in FINALIDADES:
            raise ErroDeValidacao("Escolha a finalidade da reserva.")

        with conectar() as con:
            quadra = con.execute(
                "SELECT id FROM quadra WHERE id = ? AND ativa = 1", (quadra_id,)
            ).fetchone()
            solicitante = con.execute(
                "SELECT id FROM solicitante WHERE id = ?", (solicitante_id,)
            ).fetchone()
        if quadra is None:
            raise ErroDeValidacao("Escolha uma quadra válida.")
        if solicitante is None:
            raise ErroDeValidacao("Escolha um solicitante cadastrado.")

        if Reserva.verificar_conflito(quadra["id"], data, hora_inicio, hora_fim):
            raise ErroDeValidacao(
                "Horário indisponível: já existe reserva para esta quadra nesse intervalo."
            )

        with conectar() as con:
            cursor = con.execute(
                """INSERT INTO reserva
                   (solicitante_id, quadra_id, usuario_id, data, hora_inicio, hora_fim, finalidade)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (solicitante["id"], quadra["id"], usuario_id, data, hora_inicio, hora_fim, finalidade),
            )
            return cursor.lastrowid

    @staticmethod
    def listar_do_dia(data, quadra_id=None):
        sql = """SELECT r.id, r.data, r.hora_inicio, r.hora_fim, r.finalidade, r.status,
                        q.nome AS quadra, s.nome AS solicitante, s.vinculo
                   FROM reserva r
                   JOIN quadra      q ON q.id = r.quadra_id
                   JOIN solicitante s ON s.id = r.solicitante_id
                  WHERE r.data = ?"""
        parametros = [data]
        if quadra_id:
            sql += " AND r.quadra_id = ?"
            parametros.append(quadra_id)
        sql += " ORDER BY q.nome, r.hora_inicio"
        with conectar() as con:
            return con.execute(sql, parametros).fetchall()

    @staticmethod
    def cancelar(reserva_id):
        with conectar() as con:
            cursor = con.execute(
                "UPDATE reserva SET status = 'cancelada' WHERE id = ? AND status = 'ativa'",
                (reserva_id,),
            )
            if cursor.rowcount == 0:
                raise ErroDeValidacao("Reserva não encontrada ou já cancelada.")
