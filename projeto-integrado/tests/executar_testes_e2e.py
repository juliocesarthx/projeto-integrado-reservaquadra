import json
import os
import sys
import tempfile
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))

PRINTS = os.path.join(RAIZ, "docs", "prints")
os.makedirs(PRINTS, exist_ok=True)
os.environ["RESERVAQUADRA_DB"] = os.path.join(tempfile.mkdtemp(), "e2e.db")

import seed
from werkzeug.serving import make_server

seed.popular()
from app import app

servidor = make_server("127.0.0.1", 5055, app)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:5055"
DATA = "2026-11-10"

from playwright.sync_api import sync_playwright

resultados = []


def registrar(id_, o_que, esperado, obtido, ok, print_):
    resultados.append({"id": id_, "o_que_foi_testado": o_que, "esperado": esperado,
                       "obtido": obtido, "aprovado": ok, "print": print_})
    print(f"[{'OK ' if ok else 'ERRO'}] {id_} - {o_que}: {obtido}")


def texto_alerta(page):
    alerta = page.locator(".msg")
    return alerta.first.inner_text().strip() if alerta.count() else ""


def foto(page, nome):
    page.screenshot(path=os.path.join(PRINTS, nome))
    return nome


def entrar(page, login, senha):
    page.goto(URL + "/login")
    page.fill("#login", login)
    page.fill("#senha", senha)
    page.click("button[type=submit]")


def reservar(page, solicitante, quadra, inicio, fim, finalidade="Treino", data=DATA):
    page.goto(URL + "/reservas/nova")
    page.select_option("#solicitante_id", label=solicitante)
    page.select_option("#quadra_id", label=quadra)
    page.fill("#data", data)
    page.fill("#hora_inicio", inicio)
    page.fill("#hora_fim", fim)
    if finalidade:
        page.select_option("#finalidade", label=finalidade)
    page.click("button[type=submit]")

with sync_playwright() as p:
    navegador = p.chromium.launch()
    page = navegador.new_page(viewport={"width": 1000, "height": 560}, device_scale_factor=1.5)

    page.goto(URL + "/login")
    foto(page, "fase4_login.png")

    entrar(page, "atendente", "senha-errada")
    msg = texto_alerta(page)
    ok = msg == "Login ou senha inválidos." and "/login" in page.url
    registrar("CT01", "Login com senha incorreta", "Acesso negado e mensagem de erro",
              f'Permaneceu no login; mensagem: "{msg}"', ok, foto(page, "ct01_login_invalido.png"))

    entrar(page, "atendente", "atendente123")

    page.goto(URL + "/solicitantes/novo")
    page.fill("#nome", "Carla Dias")
    page.select_option("#vinculo", label="Aluno")
    page.fill("#identificacao", "20241234")
    page.fill("#telefone", "(92) 98888-1111")
    page.fill("#email", "carla.dias@exemplo.com")
    foto(page, "fase4_solicitante_preenchido.png")
    page.click("button[type=submit]")
    msg = texto_alerta(page)
    listado = page.locator("table td", has_text="Carla Dias").count() > 0
    ok = msg == "Solicitante cadastrado com sucesso." and listado
    registrar("CT02", "Cadastro de solicitante com dados válidos", "Solicitante salvo e listado",
              f'Mensagem "{msg}"; "Carla Dias" apareceu na lista', ok, foto(page, "ct02_solicitante_valido.png"))

    page.fill("#nome", "")
    page.select_option("#vinculo", label="Professor")
    page.fill("#identificacao", "P-0999")
    page.fill("#telefone", "(92) 97777-0000")
    page.click("button[type=submit]")
    msg = texto_alerta(page)
    nao_gravou = page.locator("table td", has_text="P-0999").count() == 0
    ok = msg == "Informe o nome do solicitante." and nao_gravou
    registrar("CT03", "Cadastro de solicitante sem preencher o nome", "Mensagem de erro; solicitante não é salvo",
              f'Mensagem "{msg}"; nenhum solicitante novo na lista', ok, foto(page, "ct03_solicitante_sem_nome.png"))

    reservar(page, "Ana Souza", "Quadra Poliesportiva", "19:00", "20:00", "Treino")
    msg = texto_alerta(page)
    linha = page.locator("table tr", has_text="Ana Souza")
    conteudo = linha.inner_text() if linha.count() else ""
    ok = msg == "Reserva registrada com sucesso." and "19:00 - 20:00" in conteudo and "Treino" in conteudo
    registrar("CT04", "Reserva de quadra em horário livre (Quadra Poliesportiva, 19:00 às 20:00, Treino)",
              "Reserva gravada e listada com a finalidade informada",
              f'Mensagem "{msg}"; listagem mostra 19:00 - 20:00 e finalidade Treino', ok,
              foto(page, "ct04_reserva_livre.png"))

    reservar(page, "Prof. Bruno Lima", "Quadra Poliesportiva", "19:30", "20:30", "Aula")
    msg = texto_alerta(page)
    ok = msg.startswith("Horário indisponível") and "/reservas/nova" in page.url
    registrar("CT05", "Reserva na mesma quadra com horário sobreposto (19:30 às 20:30)",
              "Sistema impede e avisa o atendente",
              f'Reserva não gravada; mensagem: "{msg}"', ok, foto(page, "ct05_reserva_ocupada.png"))

    reservar(page, "Prof. Bruno Lima", "Quadra Society", "20:00", "19:00", "Aula")
    msg = texto_alerta(page)
    ok = msg == "O horário de fim deve ser depois do horário de início."
    registrar("CT06", "Reserva com horário de fim anterior ao início", "Mensagem de erro; não grava",
              f'Mensagem "{msg}"', ok, foto(page, "ct06_fim_antes_inicio.png"))

    reservar(page, "Prof. Bruno Lima", "Quadra Society", "20:00", "22:00", "Aula")
    reservar(page, "Ana Souza", "Quadra de Areia", "18:00", "19:00", "Uso recreativo")
    page.goto(f"{URL}/reservas?data={DATA}")
    foto(page, "fase4_listagem.png")

    page.goto(f"{URL}/reservas?data={DATA}")
    page.locator("table tr", has_text="Ana Souza").filter(has_text="Poliesportiva").locator("button").click()
    msg = texto_alerta(page)
    cancelada = page.locator("table tr", has_text="Poliesportiva").locator(".tag.cancelada").count() == 1
    reservar(page, "Prof. Bruno Lima", "Quadra Poliesportiva", "19:00", "20:00", "Aula")
    nova = texto_alerta(page)
    ok = msg.startswith("Reserva cancelada") and cancelada and nova == "Reserva registrada com sucesso."
    registrar("CT07", "Cancelar a reserva das 19:00 e reservar o mesmo horário de novo",
              "Reserva fica \"cancelada\" no histórico e o horário volta a ficar livre",
              f'Status "cancelada" exibido; nova reserva aceita ("{nova}")', ok,
              foto(page, "ct07_cancelar_liberar.png"))

    page.goto(URL + "/quadras/nova")
    msg = texto_alerta(page)
    ok = msg == "Apenas o coordenador pode acessar esta função." and "/quadras/nova" not in page.url
    registrar("CT08", "Atendente tenta abrir o cadastro de quadras",
              "Acesso negado e retorno à listagem",
              f'Redirecionado para a listagem; mensagem: "{msg}"', ok, foto(page, "ct08_acesso_restrito.png"))

    page.goto(URL + "/sair")
    entrar(page, "coordenador", "coordenador123")
    page.goto(URL + "/quadras/nova")
    page.fill("#nome", "Quadra de Beach tennis")
    page.fill("#modalidade", "Beach tennis")
    page.fill("#local", "Área externa")
    page.click("button[type=submit]")
    foto(page, "fase4_quadra_coordenador.png")
    page.goto(URL + "/reservas/nova")
    foto(page, "fase4_nova_reserva.png")

    from db import conectar
    with conectar() as con:
        linhas = con.execute(
            """SELECT r.id, s.nome AS solicitante, q.nome AS quadra, r.data, r.hora_inicio, r.hora_fim,
                      r.finalidade, r.status FROM reserva r
               JOIN solicitante s ON s.id=r.solicitante_id JOIN quadra q ON q.id=r.quadra_id ORDER BY r.id"""
        ).fetchall()
    html = ("<body style='font-family:monospace;background:#101820;color:#e6edf3;padding:16px;font-size:14px'>"
            "<div style='color:#7ee787'>sqlite&gt; SELECT r.id, s.nome, q.nome, r.data, r.hora_inicio, r.hora_fim, "
            "r.finalidade, r.status FROM reserva r JOIN ...;</div><br>"
            "<table cellpadding=6 style='border-collapse:collapse;color:#e6edf3'>"
            "<tr style='color:#79c0ff'><th>id</th><th>solicitante</th><th>quadra</th><th>data</th>"
            "<th>inicio</th><th>fim</th><th>finalidade</th><th>status</th></tr>"
            + "".join("<tr style='border-top:1px solid #30363d'>" + "".join(f"<td>{v}</td>" for v in tuple(l)) + "</tr>"
                      for l in linhas) + "</table></body>")
    page.set_viewport_size({"width": 1000, "height": 300})
    page.set_content(html)
    foto(page, "fase4_banco_sqlite.png")
    navegador.close()

servidor.shutdown()
with open(os.path.join(RAIZ, "docs", "resultados_testes.json"), "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

aprovados = sum(r["aprovado"] for r in resultados)
print(f"\n{aprovados}/{len(resultados)} casos de teste conforme esperado")
sys.exit(0 if aprovados == len(resultados) else 1)
