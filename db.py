import sqlite3
import json


class DB(object):
    def __init__(self):
        dbfile = "rss_bot.sqlite"
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()
        self.create()

    def execute(self, *args, **kwargs):
        return self.cur.execute(*args, **kwargs)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create(self):
        """ Initialize database schema """
        self.cur.executescript("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                addr        TEXT,
                url         TEXT,
                modified    BLOB
                );
        """)


def db_subscribe(addr, url, modified):
    """ Add a RSS subscription to the database.

    :param addr: (string) e-mail address
    :param url: (string) link to valid RSS feed
    :param modified: (9-tuple) dates when the RSS feed was last checked
    """
    db = DB()
    db.execute("SELECT url FROM subscriptions WHERE addr = ? AND url = ?;", (addr, url))
    # If already subscribed, raise TypeError
    if db.cur.fetchone() is not None:
        raise TypeError
    modified_json = json.dumps(modified)
    db.execute("INSERT INTO subscriptions(addr, url, modified) VALUES(?, ?, ?);",
               (addr, url, modified_json))
    db.commit()
    db.close()


def db_unsubscribe(url, addr):
    db = DB()
    db.execute("SELECT * FROM subscriptions WHERE url = ? AND addr = ?;", (url, addr))
    if db.cur.fetchone() is None:
        raise KeyError
    db.execute("DELETE FROM subscriptions WHERE url = ? AND addr = ?;", (url, addr))
    db.commit()
    db.close()


def db_list(addr):
    """ Return a string with all RSS feeds the address is subscribed to.

    :param addr: (string) e-mail address
    :return: (list of tuples(string, )) URLs to RSS feeds.
    """
    db = DB()
    db.execute("SELECT url FROM subscriptions WHERE addr = ?;", (addr, ))
    result = db.cur.fetchall()
    db.close()
    return result


def get_subscriptions():
    db = DB()
    db.execute("SELECT * FROM subscriptions;")
    result = db.cur.fetchall()
    db.close()
    # convert modified_json to tuple
    rows = []
    for row in result:
        row_list = list(row)
        modified = tuple(list(json.loads(row_list[3])))
        row_list[3] = modified
        rows.append(tuple(row_list))
    return rows


def update_modified(addr, url, modified):
    db = DB()
    modified_json = json.dumps(modified)
    db.execute("UPDATE subscriptions SET modified = ? WHERE addr = ? AND url = ?;",
               (modified_json, addr, url))
    db.commit()
    db.close()
