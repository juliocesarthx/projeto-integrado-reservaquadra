from db import conectar, criar_tabelas
from modelos import Quadra, Solicitante, Usuario


def popular():
    criar_tabelas()
    with conectar() as con:
        if con.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]:
            print("Banco já tem dados; nada a fazer.")
            return

    Usuario.criar("Marina Coordenadora", "coordenador", "coordenador123", "coordenador")
    Usuario.criar("Carlos Atendente", "atendente", "atendente123", "atendente")

    Quadra.cadastrar("Quadra Poliesportiva", "Futsal, vôlei e basquete", "Ginásio")
    Quadra.cadastrar("Quadra Society", "Futebol society", "Área externa")
    Quadra.cadastrar("Quadra de Areia", "Vôlei de praia", "Área externa")

    Solicitante.cadastrar("Ana Souza", "aluno", "20231001", "(92) 99111-2233", "ana.souza@exemplo.com")
    Solicitante.cadastrar("Prof. Bruno Lima", "professor", "P-0457", "(92) 98877-6655")
    print("Dados de demonstração criados.")

if __name__ == "__main__":
    popular()
