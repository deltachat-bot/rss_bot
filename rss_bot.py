import feedparser
from deltabot.hookspec import deltabot_hookimpl
from db import db_subscribe, db_unsubscribe, db_list, get_subscriptions, update_modified
from os import fork, getpid, kill
from time import sleep
import html2text

version = '0.1.0'


@deltabot_hookimpl
def deltabot_init(bot):
    bot.commands.register(name="/subscribe", func=subscribe)
    bot.commands.register(name="/unsubscribe", func=unsubscribe)
    bot.commands.register(name="/list", func=list)
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
        modified = feed.modified_parsed
    except KeyError:
        modified = tuple()
    try:
        etag = feed.etag
    except KeyError:
        etag = ""
    try:
        db_subscribe(contact.addr, rss_link, modified, etag)
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


def crawl(parent_pid, bot):
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
            etag = row[4]
            feed = feedparser.parse(url, modified=modified, etag=etag)
            print(url + ": " + str(feed.status))
            if feed.status == 304:
                print("No updates on " + url + ". Feed skipped.")
                continue
            for entry in feed.entries:
                infos = [entry.title,
                         "",  # Extra new line
                         "Posted at " + entry.published,
                         "Read more at " + entry.link,
                         "",  # Extra new line
                         mark_down_formatting(entry.summary, entry.link)]
                text = "\n".join(infos)
                # get chat by addr
                contact = bot.account.get_contact_by_addr(addr)
                chat = bot.account.create_chat_by_contact(contact)
                # send message to chat
                chat.send_text(text)
                if entry.updated_parsed > modified:
                    modified = entry.updated_parsed
            update_modified(addr, url, modified, feed.etag)
        sleep(120)


def mark_down_formatting(html_text, url):
    h = html2text.HTML2Text()

    # Options to transform URL into absolute links
    h.body_width = 0
    h.protect_links = True
    h.wrap_links = False
    h.baseurl = url

    md_text = h.handle(html_text)

    return md_text
