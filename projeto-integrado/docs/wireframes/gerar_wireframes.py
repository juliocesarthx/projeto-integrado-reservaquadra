import os

from playwright.sync_api import sync_playwright

PASTA = os.path.dirname(os.path.abspath(__file__))

CSS = """
*{box-sizing:border-box} body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#444}
.tela{width:900px;height:520px;border:3px solid #555;margin:10px;position:relative;background:#fafafa}
.topo{height:46px;border-bottom:2px solid #555;background:#e4e4e4;display:flex;align-items:center;gap:22px;padding:0 18px;font-size:14px}
.logo{font-weight:bold;border:2px solid #555;padding:3px 10px;background:#fff}
.menu{border-bottom:2px dashed #888;padding:2px 4px}
.dir{margin-left:auto;font-size:13px}
.corpo{padding:20px 28px}
h2{margin:0 0 14px;font-size:20px;color:#333}
.campo{margin:10px 0}.campo label{display:block;font-size:13px;margin-bottom:3px}
.caixa{height:32px;border:2px solid #777;background:#fff;padding:6px 8px;font-size:13px;color:#999}
.linha{display:flex;gap:16px}.linha>div{flex:1}
.botao{display:inline-block;border:2px solid #444;background:#cfcfcf;padding:8px 20px;font-size:14px;font-weight:bold;margin-top:10px}
.aviso{border:2px dashed #888;padding:8px 12px;font-size:13px;margin-bottom:12px;background:#f0f0f0}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
th,td{border:2px solid #777;padding:7px 8px;text-align:left}th{background:#e4e4e4}
.cartao{border:2px solid #777;padding:14px 18px;margin-bottom:14px;background:#fff}
.nota{position:absolute;right:14px;bottom:10px;font-size:12px;color:#777}
"""

TOPO = ('<div class="topo"><span class="logo">ReservaQuadra</span><span class="menu">Reservas do dia</span>'
        '<span class="menu">Nova reserva</span><span class="menu">Solicitantes</span>{quadras}'
        '<span class="dir">[Nome do usuário] &nbsp; Sair</span></div>')


def tela(corpo, quadras=False, topo=True, rotulo=""):
    t = TOPO.format(quadras='<span class="menu">Quadras</span>' if quadras else "") if topo else ""
    return f'<div class="tela">{t}<div class="corpo">{corpo}</div><div class="nota">{rotulo}</div></div>'

TELAS = {
    "tela1_login": tela(
        '<div class="cartao" style="width:360px;margin:60px auto"><h2>ReservaQuadra</h2>'
        '<div class="campo"><label>Login</label><div class="caixa">usuário</div></div>'
        '<div class="campo"><label>Senha</label><div class="caixa">••••••</div></div>'
        '<div class="botao">Entrar</div></div>', topo=False, rotulo="Tela 1 - Login"),
    "tela2_cadastro_solicitante": tela(
        '<div class="cartao"><h2>Novo solicitante</h2>'
        '<div class="linha"><div class="campo"><label>Nome</label><div class="caixa">nome completo</div></div>'
        '<div class="campo"><label>Vínculo</label><div class="caixa">Selecione... &nbsp; ▼</div></div>'
        '<div class="campo"><label>Matrícula, RA ou crachá</label><div class="caixa">identificação</div></div></div>'
        '<div class="linha"><div class="campo"><label>Telefone (com DDD)</label><div class="caixa">(__) _____-____</div></div>'
        '<div class="campo"><label>E-mail (opcional)</label><div class="caixa">nome@email.com</div></div></div>'
        '<div class="botao">Salvar solicitante</div></div>'
        '<div class="cartao"><b>Solicitantes cadastrados</b><table><tr><th>Nome</th><th>Vínculo</th><th>Identificação</th><th>Telefone</th></tr>'
        '<tr><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td></tr><tr><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td></tr></table></div>',
        rotulo="Tela 2 - Cadastro de solicitante"),
    "tela3_cadastro_quadra": tela(
        '<div class="cartao"><h2>Nova quadra</h2><div class="linha">'
        '<div class="campo"><label>Nome da quadra</label><div class="caixa">Quadra 1</div></div>'
        '<div class="campo"><label>Modalidade</label><div class="caixa">Futsal</div></div>'
        '<div class="campo"><label>Local (opcional)</label><div class="caixa">bloco ou área</div></div></div>'
        '<div class="botao">Salvar quadra</div></div>'
        '<div class="cartao"><b>Quadras ativas</b><table><tr><th>Nome</th><th>Modalidade</th><th>Local</th></tr>'
        '<tr><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td></tr><tr><td>xxxxxxxx</td><td>xxxxxxxx</td><td>xxxxxxxx</td></tr></table></div>',
        quadras=True, rotulo="Tela 3 - Cadastro de quadra (somente coordenador)"),
    "tela4_nova_reserva": tela(
        '<div class="aviso">[Área de mensagem: erro ou sucesso]</div>'
        '<div class="cartao"><h2>Nova reserva</h2><div class="linha">'
        '<div class="campo"><label>Solicitante</label><div class="caixa">Selecione... &nbsp; ▼</div></div>'
        '<div class="campo"><label>Quadra</label><div class="caixa">Selecione... &nbsp; ▼</div></div></div>'
        '<div class="linha"><div class="campo"><label>Data</label><div class="caixa">dd/mm/aaaa</div></div>'
        '<div class="campo"><label>Início</label><div class="caixa">hh:mm</div></div>'
        '<div class="campo"><label>Fim</label><div class="caixa">hh:mm</div></div>'
        '<div class="campo"><label>Finalidade</label><div class="caixa">Selecione... &nbsp; ▼</div></div></div>'
        '<div class="botao">Reservar</div></div>', rotulo="Tela 4 - Nova reserva"),
    "tela5_reservas_do_dia": tela(
        '<div class="cartao"><h2>Reservas do dia</h2><div class="linha" style="align-items:flex-end">'
        '<div class="campo"><label>Data</label><div class="caixa">dd/mm/aaaa</div></div>'
        '<div class="campo"><label>Quadra</label><div class="caixa">Todas &nbsp; ▼</div></div>'
        '<div><span class="botao">Filtrar</span></div><div style="text-align:right"><span class="botao">+ Nova reserva</span></div></div></div>'
        '<div class="cartao"><table><tr><th>Horário</th><th>Quadra</th><th>Solicitante</th><th>Finalidade</th><th>Status</th><th></th></tr>'
        '<tr><td>hh:mm - hh:mm</td><td>xxxxxx</td><td>xxxxxx</td><td>xxxxxx</td><td>ativa</td><td>[Cancelar]</td></tr>'
        '<tr><td>hh:mm - hh:mm</td><td>xxxxxx</td><td>xxxxxx</td><td>xxxxxx</td><td>ativa</td><td>[Cancelar]</td></tr>'
        '<tr><td>hh:mm - hh:mm</td><td>xxxxxx</td><td>xxxxxx</td><td>xxxxxx</td><td>cancelada</td><td></td></tr></table></div>',
        rotulo="Tela 5 - Reservas do dia"),
}

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={"width": 920, "height": 540}, device_scale_factor=1.5)
    for nome, corpo in TELAS.items():
        pg.set_content(f"<style>{CSS}</style>{corpo}")
        pg.screenshot(path=os.path.join(PASTA, f"{nome}.png"))
        print(nome, "ok")
    nav.close()
