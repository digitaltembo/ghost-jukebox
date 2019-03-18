
-- table to store key/value pairs
CREATE TABLE info(
    key TEXT,
    value TEXT
);

-- table to store QR code info
CREATE TABLE qr_codes(
    code TEXT,
    type INT,
    uri TEXT,
    title TEXT
);