import feedparser
from deltabot.hookspec import deltabot_hookimpl

version = '0.1.0'


@deltabot_hookimpl
def deltabot_init(bot):
    bot.commands.register(name="/subscribe", func=subscribe)
    bot.commands.register(name="/unsubscribe", func=unsubscribe)


def subscribe(command):
    """ Subscribes contact to a given RSS feed.

    To use it, tell the bot the RSS feed link, starting with "/subscribe".
    Example: "/subscribe https://delta.chat/feed.xml"
    """
    contact = command.message.get_sender_contact()
    rss_link = command.payload
    feed = feedparser.parse(rss_link)
    try:
        db_save(rss_link, contact.addr, feed.modified)
    except AttributeError:
        return "No valid RSS feed found at " + rss_link
    return "Successfully subscribed to " + rss_link + "\n\n"


def unsubscribe(command):
    """ Unsubscribes contact from a given RSS feed.

    To use it, tell the bot the RSS feed link, starting with "/unsubscribe".
    Example: "/unsubscribe https://delta.chat/feed.xml"
    """
    pass


def post(filter):
    pass


def crawl():
    pass


def db_save(url, addr, modified):
    pass
