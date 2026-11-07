import os
from datetime import date
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from db import criar_tabelas
from modelos import FINALIDADES, VINCULOS, ErroDeValidacao, Quadra, Reserva, Solicitante, Usuario

app = Flask(__name__)
app.secret_key = os.environ.get("RESERVAQUADRA_SECRET", "troque-esta-chave-em-producao")


def login_obrigatorio(rota):
    @wraps(rota)
    def protegida(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return rota(*args, **kwargs)
    return protegida


def coordenador_obrigatorio(rota):
    @wraps(rota)
    def protegida(*args, **kwargs):
        if session.get("perfil") != "coordenador":
            flash("Apenas o coordenador pode acessar esta função.", "erro")
            return redirect(url_for("listar_reservas"))
        return rota(*args, **kwargs)
    return protegida

@app.route("/login", methods=["GET", "POST"])


def login():
    if request.method == "POST":
        usuario = Usuario.autenticar(request.form.get("login", ""), request.form.get("senha", ""))
        if usuario:
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            session["perfil"] = usuario["perfil"]
            return redirect(url_for("listar_reservas"))
        flash("Login ou senha inválidos.", "erro")
    return render_template("login.html")

@app.route("/sair")


def sair():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")


def inicio():
    return redirect(url_for("listar_reservas"))

@app.route("/solicitantes/novo", methods=["GET", "POST"])
@login_obrigatorio


def novo_solicitante():
    if request.method == "POST":
        try:
            Solicitante.cadastrar(
                request.form.get("nome"),
                request.form.get("vinculo"),
                request.form.get("identificacao"),
                request.form.get("telefone"),
                request.form.get("email"),
            )
            flash("Solicitante cadastrado com sucesso.", "ok")
            return redirect(url_for("novo_solicitante"))
        except ErroDeValidacao as erro:
            flash(str(erro), "erro")
    return render_template(
        "solicitante_form.html", solicitantes=Solicitante.listar(), vinculos=VINCULOS, form=request.form
    )

@app.route("/quadras/nova", methods=["GET", "POST"])
@login_obrigatorio
@coordenador_obrigatorio


def nova_quadra():
    if request.method == "POST":
        try:
            Quadra.cadastrar(
                request.form.get("nome"), request.form.get("modalidade"), request.form.get("local")
            )
            flash("Quadra cadastrada com sucesso.", "ok")
            return redirect(url_for("nova_quadra"))
        except ErroDeValidacao as erro:
            flash(str(erro), "erro")
    return render_template("quadra_form.html", quadras=Quadra.listar_ativas(), form=request.form)

@app.route("/reservas/nova", methods=["GET", "POST"])
@login_obrigatorio


def nova_reserva():
    if request.method == "POST":
        try:
            Reserva.registrar(
                solicitante_id=request.form.get("solicitante_id", type=int),
                quadra_id=request.form.get("quadra_id", type=int),
                usuario_id=session["usuario_id"],
                data=request.form.get("data"),
                hora_inicio=request.form.get("hora_inicio"),
                hora_fim=request.form.get("hora_fim"),
                finalidade=request.form.get("finalidade"),
            )
            flash("Reserva registrada com sucesso.", "ok")
            return redirect(url_for("listar_reservas", data=request.form.get("data")))
        except ErroDeValidacao as erro:
            flash(str(erro), "erro")
    return render_template(
        "reserva_form.html",
        solicitantes=Solicitante.listar(),
        quadras=Quadra.listar_ativas(),
        finalidades=FINALIDADES,
        form=request.form,
        hoje=date.today().isoformat(),
    )

@app.route("/reservas")
@login_obrigatorio


def listar_reservas():
    data = request.args.get("data") or date.today().isoformat()
    quadra_id = request.args.get("quadra_id", type=int)
    return render_template(
        "reserva_lista.html",
        reservas=Reserva.listar_do_dia(data, quadra_id),
        quadras=Quadra.listar_ativas(),
        finalidades=FINALIDADES,
        data=data,
        quadra_id=quadra_id,
    )

@app.route("/reservas/<int:reserva_id>/cancelar", methods=["POST"])
@login_obrigatorio


def cancelar_reserva(reserva_id):
    try:
        Reserva.cancelar(reserva_id)
        flash("Reserva cancelada. O horário está livre novamente.", "ok")
    except ErroDeValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("listar_reservas", data=request.form.get("data")))

criar_tabelas()

if __name__ == "__main__":
    app.run(debug=True)
