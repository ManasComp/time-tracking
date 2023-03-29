"""SQLite Database module for application."""
import io
import sqlite3

import click
from flask import current_app, g


SERVER_ADDRESS = "/database/backupdatabase.sql"

def init_app(app):
    """Initialize the application with the database."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    """Get the database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def backup_db():
    """Backup the database."""
    print("backing up db")
    try:
        with io.open(SERVER_ADDRESS, 'w') as p:
            for line in get_db().iterdump():
                p.write('%s\n' % line)
    except:
        print("backup failed")
    print("backup done")


def close_db(e=None):
    """Close the database connection."""
    print("closing db")
    backup_db()
    database = g.pop("db", None)

    if database is not None:
        database.close()


def init_db():
    """Initialize the database."""

    database = get_db()
   
    try:
        with io.open(SERVER_ADDRESS, 'r') as p:
            database.executescript(p.read()).decode("utf8")
    except (Exception) as error:
        with open("error.txt", "w") as error_file:
            error_file.write(str(error))
        try:
            with current_app.open_resource("schema.sql") as database_file:
                database.executescript(database_file.read().decode("utf8"))
        except:
            print("backup load failed")
        print("backup load failed")

    backup_db()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
