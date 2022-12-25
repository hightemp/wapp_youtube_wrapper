DROP TABLE IF EXISTS youtube_search_words;
CREATE TABLE youtube_search_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

DROP TABLE IF EXISTS youtube_found;
CREATE TABLE youtube_found (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_search_words_id INTEGER NULL,
    youtube_id TEXT NOT NULL,
    url TEXT NULL
);

DROP TABLE IF EXISTS update_queue;
CREATE TABLE update_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NULL,
    started_at INTEGER NULL,
    stopped_at INTEGER NULL,
    update_status INTEGER NULL,
    youtube_search_words_id INTEGER NULL
);
