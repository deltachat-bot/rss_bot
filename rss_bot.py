import feedparser
from deltabot.hookspec import deltabot_hookimpl
from db import db_subscribe, db_unsubscribe, db_list, get_subscriptions, update_modified
from os import fork, getpid, kill
from time import sleep
import html2text
from bs4 import BeautifulSoup


version = '0.1.1'


@deltabot_hookimpl
def deltabot_init(bot):
    """ Init function of the bot, gets called by deltabot. It registers commands and starts the crawl loop.

    :param bot (deltabot.Deltabot object) the Deltabot object of this particular bot.
    """
    bot.commands.register(name="/subscribe", func=subscribe)
    bot.commands.register(name="/unsubscribe", func=unsubscribe)
    bot.commands.register(name="/list", func=list_feeds)
    # Start RSS feed crawling loop in a new process:
    parent_pid = getpid()
    if not fork():
        crawl(parent_pid, bot)


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
        db_subscribe(contact.addr, rss_link, feed.modified_parsed)
    except AttributeError:  # not sure whether this is enough to check RSS validity
        return "No valid RSS feed found at " + rss_link
    except TypeError:
        return "You are already subscribed to " + rss_link
    return "Success: you subscribed to " + rss_link


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
    return "You have unsubscribed from " + rss_link


def list_feeds(command):
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


def crawl(parent_pid, bot):
    """ Never ending loop which crawls new RSS messages once a minute, and sends them to subscribers.

    :param parent_pid (integer) This is a fork of the deltabot process; exit if parent process dies.
    :param bot (deltabot.Deltabot object) the Deltabot object of this particular bot.
    """
    while 1:
        # exit cleanly if parent process stopped
        try:
            kill(parent_pid, 0)
        except OSError:
            exit(0)
        subscriptions = get_subscriptions()
        for row in subscriptions:
            addr = row[1]
            url = row[2]
            modified = row[3]
            newest_date = modified
            feed = feedparser.parse(url, modified=modified)
            try:
                if feed.status == 304:
                    continue
            except AttributeError:
                pass
            for entry in feed.entries:
                text = format_entry(entry)
                # get chat by addr
                contact = bot.account.get_contact_by_addr(addr)
                chat = bot.account.create_chat_by_contact(contact)
                # send message to chat
                try:
                    if entry.updated_parsed > newest_date:
                        chat.send_text(text)
                    # update the date of the last modified message
                    if entry.updated_parsed > modified:
                        modified = entry.updated_parsed
                except AttributeError:
                    pass  # no updated date value
            update_modified(addr, url, modified)
        sleep(60)


def format_entry(entry):
    """ This function formats the HTML output of RSS feeds to beautiful Delta messages.

    :param entry (dictionary) An RSS feed entry dictionary returned by feedparser.parse()
    :return: text (string) a formatted Delta Chat message to be sent to the user
    """
    # remove images and link tags
    soup = BeautifulSoup(entry.summary)
    try:
        soup.img.decompose()
    except AttributeError:
        pass  # no img tags
    try:
        soup.a.unwrap()
    except AttributeError:
        pass  # no a tags

    # convert HTML to markdown
    h = html2text.HTML2Text()
    # Options to transform URL into absolute links
    h.body_width = 0
    h.protect_links = True
    h.wrap_links = False
    h.baseurl = entry.link
    md_text = h.handle(str(soup))

    # Create message out of entry attributes
    parts = []
    try:
        parts.append(entry.title)
    except AttributeError:
        pass
    parts.append("")  # Extra new line
    try:
        parts.append("Posted at " + entry.published)
    except AttributeError:
        pass
    try:
        parts.append("Read more at " + entry.link)
    except AttributeError:
        pass
    parts.append("")  # Extra new line
    parts.append(md_text)
    text = "\n".join(parts)

    return text
