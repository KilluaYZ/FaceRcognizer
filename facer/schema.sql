DROP TABLE IF EXISTS faces;
CREATE TABLE faces(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	facename TEXT NOT NULL,
	facearray TEXT NOT NULL
);
