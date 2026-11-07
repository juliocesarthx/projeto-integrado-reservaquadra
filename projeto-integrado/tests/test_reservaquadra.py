import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

@pytest.fixture()


def ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("RESERVAQUADRA_DB", str(tmp_path / "teste.db"))
    import seed
    seed.popular()
    from db import conectar
    with conectar() as con:
        usuario_id = con.execute("SELECT id FROM usuario WHERE login='atendente'").fetchone()[0]
        quadra_id = con.execute("SELECT id FROM quadra ORDER BY id LIMIT 1").fetchone()[0]
        solicitante_id = con.execute("SELECT id FROM solicitante ORDER BY id LIMIT 1").fetchone()[0]
    return {"usuario": usuario_id, "quadra": quadra_id, "solicitante": solicitante_id}


def reservar(a, inicio, fim, finalidade="treino", data="2026-11-10"):
    from modelos import Reserva
    return Reserva.registrar(a["solicitante"], a["quadra"], a["usuario"], data, inicio, fim, finalidade)


def test_rf02_cadastro_de_solicitante_valido(ambiente):
    from modelos import Solicitante
    novo_id = Solicitante.cadastrar("Carla Dias", "aluno", "20241234", "(92) 98888-1111", "carla@exemplo.com")
    assert novo_id > 0
    assert "Carla Dias" in [s["nome"] for s in Solicitante.listar()]


def test_rf02_cadastro_de_solicitante_sem_nome(ambiente):
    from modelos import ErroDeValidacao, Solicitante
    antes = len(Solicitante.listar())
    with pytest.raises(ErroDeValidacao):
        Solicitante.cadastrar("   ", "aluno", "20241234", "(92) 98888-1111")
    assert len(Solicitante.listar()) == antes


def test_rf02_vinculo_e_identificacao_obrigatorios(ambiente):
    from modelos import ErroDeValidacao, Solicitante
    with pytest.raises(ErroDeValidacao):
        Solicitante.cadastrar("Carla Dias", "visitante", "20241234", "(92) 98888-1111")
    with pytest.raises(ErroDeValidacao):
        Solicitante.cadastrar("Carla Dias", "aluno", "  ", "(92) 98888-1111")


def test_rf04_reserva_em_horario_livre(ambiente):
    from modelos import Reserva
    reservar(ambiente, "19:00", "20:00", "aula")
    lista = Reserva.listar_do_dia("2026-11-10")
    assert len(lista) == 1 and lista[0]["finalidade"] == "aula" and lista[0]["status"] == "ativa"


def test_rf04_finalidade_obrigatoria(ambiente):
    from modelos import ErroDeValidacao
    with pytest.raises(ErroDeValidacao):
        reservar(ambiente, "19:00", "20:00", finalidade="")


def test_rf05_reserva_em_horario_ocupado(ambiente):
    from modelos import ErroDeValidacao, Reserva
    reservar(ambiente, "19:00", "20:00")
    with pytest.raises(ErroDeValidacao):
        reservar(ambiente, "19:30", "20:30")
    assert len(Reserva.listar_do_dia("2026-11-10")) == 1


def test_rf04_hora_fim_antes_do_inicio(ambiente):
    from modelos import ErroDeValidacao, Reserva
    with pytest.raises(ErroDeValidacao):
        reservar(ambiente, "20:00", "19:00")
    assert Reserva.listar_do_dia("2026-11-10") == []


def test_rf07_cancelar_libera_o_horario(ambiente):
    from modelos import Reserva
    rid = reservar(ambiente, "19:00", "20:00")
    Reserva.cancelar(rid)

    reservar(ambiente, "19:00", "20:00")
    status = sorted(r["status"] for r in Reserva.listar_do_dia("2026-11-10"))
    assert status == ["ativa", "cancelada"]


def test_reservas_encostadas_nao_conflitam(ambiente):
    from modelos import Reserva
    reservar(ambiente, "18:00", "19:00")
    reservar(ambiente, "19:00", "20:00")
    assert len(Reserva.listar_do_dia("2026-11-10")) == 2


def test_login_valido_e_invalido(ambiente):
    from modelos import Usuario
    assert Usuario.autenticar("atendente", "atendente123") is not None
    assert Usuario.autenticar("atendente", "errada") is None


def test_senha_nao_fica_em_texto_puro(ambiente):
    from db import conectar
    with conectar() as con:
        hashes = [l[0] for l in con.execute("SELECT senha_hash FROM usuario")]
    assert all("123" not in h for h in hashes)
