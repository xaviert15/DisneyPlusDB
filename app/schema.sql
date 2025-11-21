PRAGMA foreign_keys = ON;

-- 1. Tabelas de Lookup (Simples e diretas)
CREATE TABLE IF NOT EXISTS Rating (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE  -- Ex: PG-13, TV-MA
);

CREATE TABLE IF NOT EXISTS Genre (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Country (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Person (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- 2. Tabela Principal (A grande mudança)
-- Em vez de espalhar dados por 3 tabelas, centralizamos aqui.
CREATE TABLE IF NOT EXISTS Show (
    show_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    
    -- Tipo de conteúdo (Movie vs TV Show)
    show_type TEXT CHECK(show_type IN ('Movie', 'TV Show')) NOT NULL,
    
    -- Data (O ano extrai-se daqui com strftime('%Y', release_date))
    release_date DATE, 
    date_added DATE,
    
    -- Duração (Atributos diretos, sem tabelas externas malucas)
    duration_value INTEGER, -- ex: 90 ou 2
    duration_unit TEXT,     -- ex: 'min' ou 'Seasons'
    
    rating_id INTEGER,
    FOREIGN KEY (rating_id) REFERENCES Rating(rating_id)
);

-- 3. Tabelas de Associação (Many-to-Many)

-- Substitui a tabela "Paper". "Credit" é o termo técnico correto.
CREATE TABLE IF NOT EXISTS Credit (
    show_id INTEGER,
    person_id INTEGER,
    role TEXT NOT NULL, -- 'Director' ou 'Actor'
    PRIMARY KEY (show_id, person_id, role),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (person_id) REFERENCES Person(person_id)
);

-- Substitui a "ListedIn"
CREATE TABLE IF NOT EXISTS Show_Genre (
    show_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (show_id, genre_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
);

-- Substitui a "StreamingOn"
CREATE TABLE IF NOT EXISTS Show_Country (
    show_id INTEGER,
    country_id INTEGER,
    PRIMARY KEY (show_id, country_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);