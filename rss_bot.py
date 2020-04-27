import feedparser
from deltabot.hookspec import deltabot_hookimpl
from db import db_subscribe, db_unsubscribe, db_list

version = '0.1.0'


@deltabot_hookimpl
def deltabot_init(bot):
    bot.commands.register(name="/subscribe", func=subscribe)
    bot.commands.register(name="/unsubscribe", func=unsubscribe)
    bot.commands.register(name="/list", func=list)


def subscribe(command):
    """ Subscribes you to a given RSS feed.

    To use it, tell the bot the RSS feed link, starting with "/subscribe".
    Example: "/subscribe https://delta.chat/feed.xml"
    :return: String which gets replied to the user
    """
    contact = command.message.get_sender_contact()
    rss_link = command.payload
    feed = feedparser.parse(rss_link)
    try:
        db_subscribe(contact.addr, rss_link, feed.modified)
    except AttributeError:  # not sure whether this is enough to check RSS validity
        return "No valid RSS feed found at " + rss_link
    return "Successfully subscribed to " + rss_link + "\n\n"


def unsubscribe(command):
    """ Unsubscribes you from a given RSS feed.

    To use it, tell the bot the RSS feed link, starting with "/unsubscribe".
    Example: "/unsubscribe https://delta.chat/feed.xml"
    :return: String which gets replied to the user
    """
    contact = command.message.get_sender_contact()
    rss_link = command.payload
    try:
        db_unsubscribe(rss_link, contact.addr)
    except KeyError:
        return "No subscription found - have you typed the link correctly?"
    return "Successfully unsubscribed from " + rss_link


def list(command):
    """ List all RSS feeds you are subscribed to.

    To use it, just send "/list" to the bot.
    :return: String which gets replied to the user
    """
    replylist = ["You are subscribed to these RSS feeds:"]
    for url in db_list(command.message.get_sender_contact().addr):
        replylist.append(url[0])
    if len(replylist) == 1:
        return "You aren't subscribed to any RSS feeds yet. Type '/help' to find out how to use this bot."
    return "\n".join(replylist)


def post(filter):
    pass


def crawl():
    pass
