#!/usr/bin/python3

import getopt
import sqlite3
import sys

from flaskr import task


def create_connection(db_file):
    """create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("err")

    return conn


def main(argv):
    category = ""
    comment = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("test.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("test.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            category = arg
        elif opt in ("-o", "--ofile"):
            comment = arg
    print('Input file is "', category)
    print('Output file is "', comment)
    database = r"instance/flaskr.sqlite"

    # create a database connection
    conn = create_connection(database)
    with conn:
        if task.get_count_of_active_tasks_for_user(conn, 1) != 1:
            print("error")
        else:
            task.end_last_active_task_for_user(conn, 1, category, comment)


if __name__ == "__main__":
    main(sys.argv[1:])
