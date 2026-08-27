CREATE TABLE games (
    id UUID PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0),
    answered INTEGER NOT NULL DEFAULT 0 CHECK (answered >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'playing',
    game_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
