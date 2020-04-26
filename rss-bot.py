import feedparser
from deltabot.hookspec import deltabot_hookimpl


version = '1.0'


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
    print(rss_link)
    print(contact)
    # add rss_link + contact_id to database
    # reply with "successfully subscribed to https://delta.chat/feed.xml"

def unsubscribe(command):
    pass

def post(command):
    pass

def crawl():
    pass

