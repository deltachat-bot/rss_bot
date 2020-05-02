import sqlite3
import json
import os


class DB(object):
    def __init__(self, bot):
        """ Create a DB object to manage connections.

        Each function can create their own DB object.
        Please close the connection at the end of the function.
        """
        dbfile = os.path.join(get_dir(bot), "rss_bot.sqlite")
        self.conn = sqlite3.connect(dbfile)
        self.cur = self.conn.cursor()
        self.create()

    def execute(self, *args, **kwargs):
        """ Shortcut function to execute sqlite commands. """
        return self.cur.execute(*args, **kwargs)

    def commit(self):
        """ Shortcut function to commit executed changes to the DB. """
        self.conn.commit()

    def close(self):
        """ Shortcut function to close the DB. """
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


def db_subscribe(bot, addr, url, modified):
    """ DB call to add a RSS subscription to the database. Called by rss_bot.subscribe()

    :param addr: (string) e-mail address of the subscriber
    :param url: (string) link to valid RSS feed
    :param modified: (9-tuple) dates when the RSS feed was last modified
    """
    db = DB(bot)
    db.execute("SELECT url FROM subscriptions WHERE addr = ? AND url = ?;", (addr, url))
    # If already subscribed, raise TypeError
    if db.cur.fetchone() is not None:
        raise TypeError
    modified_json = json.dumps(modified)
    db.execute("INSERT INTO subscriptions(addr, url, modified) VALUES(?, ?, ?);",
               (addr, url, modified_json))
    db.commit()
    db.close()


def db_unsubscribe(bot, url, addr):
    """ DB call to unsubscribe users from feeds. Called by rss_bot.unsubscribe()

    Raises a Key Error if no subscription is found.
    :param url: (string) URL of the RSS Feed to unsubscribe from
    :param addr: (string) email address of the subscriber
    """
    db = DB(bot)
    db.execute("SELECT * FROM subscriptions WHERE url = ? AND addr = ?;", (url, addr))
    if db.cur.fetchone() is None:
        raise KeyError
    db.execute("DELETE FROM subscriptions WHERE url = ? AND addr = ?;", (url, addr))
    db.commit()
    db.close()


def db_list(bot, addr):
    """ Return a string with all RSS feeds the address is subscribed to. Called by rss_bot.list_feeds()

    :param addr: (string) e-mail address
    :return: (list of tuples(string, )) URLs to RSS feeds.
    """
    db = DB(bot)
    db.execute("SELECT url FROM subscriptions WHERE addr = ?;", (addr, ))
    result = db.cur.fetchall()
    db.close()
    return result


def get_subscriptions(bot):
    """ DB call to get all subscriptions. Called by rss_bot.crawl()

    :return: rows: (list of tuples) All subscriptions the bot knows of.
    """
    db = DB(bot)
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


def update_modified(bot, addr, url, modified):
    """ DB call to update the date when a RSS feed was last modified. Called by rss_bot.crawl()

    :param addr: (string) e-mail address of the subscriber
    :param url: (string) link to valid RSS feed
    :param modified: (9-tuple) dates when the RSS feed was last modified
    """
    db = DB(bot)
    modified_json = json.dumps(modified)
    db.execute("UPDATE subscriptions SET modified = ? WHERE addr = ? AND url = ?;",
               (modified_json, addr, url))
    db.commit()
    db.close()


def get_dir(bot):
    path = os.path.join(os.path.dirname(bot.account.db_path))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

