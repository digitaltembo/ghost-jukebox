
-- table to store key/value pairs
CREATE TABLE info(
    key   TEXT,
    value TEXT
);

-- table to store Card info
CREATE TABLE cards(
    code      TEXT,
    card_type INT,
    item_id   TEXT,
    title     TEXT
);

-- table used to store the music queue, pretty straightforward
CREATE TABLE queue(
    thing TEXT
);