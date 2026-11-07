PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    login       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL,
    perfil      TEXT    NOT NULL CHECK (perfil IN ('atendente', 'coordenador'))
);

CREATE TABLE IF NOT EXISTS solicitante (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    vinculo       TEXT NOT NULL CHECK (vinculo IN ('aluno', 'professor', 'colaborador')),
    identificacao TEXT NOT NULL,
    telefone      TEXT NOT NULL,
    email         TEXT
);

CREATE TABLE IF NOT EXISTS quadra (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL UNIQUE,
    modalidade  TEXT NOT NULL,
    local       TEXT,
    ativa       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reserva (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitante_id  INTEGER NOT NULL REFERENCES solicitante(id),
    quadra_id       INTEGER NOT NULL REFERENCES quadra(id),
    usuario_id      INTEGER NOT NULL REFERENCES usuario(id),
    data            TEXT    NOT NULL,
    hora_inicio     TEXT    NOT NULL,
    hora_fim        TEXT    NOT NULL,
    finalidade      TEXT    NOT NULL CHECK (finalidade IN ('aula', 'treino', 'evento', 'lazer')),
    status          TEXT    NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa', 'cancelada'))
);

CREATE INDEX IF NOT EXISTS idx_reserva_quadra_data ON reserva (quadra_id, data);
