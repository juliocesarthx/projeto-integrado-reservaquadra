# Projeto Integrado: Sistema de Reserva de Quadras

Trabalho acadêmico desenvolvido para o Projeto Integrado do curso de ADS

## Sobre o projeto

Sistema web para reservar as quadras esportivas de uma faculdade. Permite cadastrar solicitantes (alunos, professores e colaboradores) e quadras, registrar reservas com finalidade e horário, impedir conflitos de horário, consultar as reservas do dia e cancelar reservas.

O trabalho cobre as etapas do Projeto Integrado: levantamento de requisitos, modelagem (casos de uso, classes, MER e sequência), protótipos de tela, desenvolvimento com banco de dados e testes.

## Tecnologias

- Python 3
- Flask
- SQLite

## Como executar

O código do sistema está na pasta `projeto-integrado`.

```bash
cd projeto-integrado
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/seed.py
python app/app.py
```

Depois, abra http://127.0.0.1:5000 no navegador.

Usuários de demonstração: `atendente / atendente123` e `coordenador / coordenador123`.

## Testes

```bash
python -m pytest -v
```

## Observação

Projeto desenvolvido para fins acadêmicos.
