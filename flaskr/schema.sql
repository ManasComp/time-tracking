DROP TABLE IF EXISTS post;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS user_role;

CREATE TABLE user_role (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  role TEXT UNIQUE NOT NULL
);

INSERT INTO user_role (role) VALUES('User');
INSERT INTO user_role (role) VALUES('Admin');

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  role_id INTEGER NOT NULL DEFAULT 1,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  FOREIGN KEY (role_id) REFERENCES user_role (id)
);

INSERT INTO user (role_id, username, password) VALUES(2, "Ondrej", "pbkdf2:sha256:260000$Qredm6S7rWsERXHP$f707c910a190a6ce8e335549c7f8116f3c8702109a1303edea8b7924005787cf");

CREATE TABLE task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  duration INTEGER NOT NULL DEFAULT 0,
  author_id INTEGER NOT NULL,
  category TEXT NOT NULL DEFAULT "UNDEFINED",
  comment TEXT NOT NULL DEFAULT "",
  finished BOOLEAN NOT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
  event_category TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES task (id)
);

