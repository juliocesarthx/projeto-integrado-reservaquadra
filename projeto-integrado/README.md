# ReservaQuadra - Projeto Integrado

Sistema web para reservar as quadras esportivas de uma faculdade (solicitantes: alunos, professores e colaboradores).
Python 3 + Flask + SQLite. Usuário de demonstração: `atendente / atendente123` e `coordenador / coordenador123`.

## Como rodar (Windows, macOS ou Linux)

```bash
python -m venv .venv

pip install -r requirements.txt
python app/seed.py          
python app/app.py           
```

## Testes

```bash
python -m pytest -v                       
playwright install chromium               
python tests/executar_testes_e2e.py       
```

## Regenerar diagramas e protótipos

```bash
python docs/diagramas/fontes/gerar_casos_de_uso.py   
python docs/wireframes/gerar_wireframes.py           
```

Classes, MER e sequência estão em `docs/diagramas/fontes/*.mmd` (texto Mermaid, editável em mermaid.live).

## Estrutura

| Pasta/arquivo | Conteúdo |
| --- | --- |
| `app/schema.sql` | Tabelas do banco (MER) |
| `app/modelos.py` | Classes e regras de negócio |
| `app/app.py` | Rotas web e controle de acesso |
| `app/templates/` | As 5 telas |
| `tests/` | Testes automatizados e execução no navegador |
| `docs/diagramas/` | Casos de uso, classes, MER e sequência (PNG + fontes editáveis) |
| `docs/wireframes/` | Protótipos das 5 telas |
| `docs/prints/` | Evidências de execução e dos testes |

## Requisitos atendidos

RF01 login - RF02 cadastrar solicitante - RF03 cadastrar quadra (coordenador) - RF04 reservar quadra com finalidade -
RF05 impedir conflito de horário - RF06 listar reservas do dia - RF07 cancelar reserva.
