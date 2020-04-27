# RSS-Bot for Delta Chat

This is a bot to read RSS feeds within Delta Chat.

With "/subscribe https://delta.chat/feed.xml" you can subscribe to an RSS feed,
with "/unsubscribe https://delta.chat/feed.xml" you can stop receiving updates
from that feed.

With "/list" you can see all RSS feeds you are currently subscribed to.
The bot looks up those feeds regularly and sends you new posts per Delta
message.

## Running it Yourself

To setup the bot, clone this repository, install it, initialize it with an
email address, and run it:

```bash
git clone http://github.com/deltachat-bot/rss_bot
cd rss_bot
virtualenv -p python3 venv
. venv/bin/activate
pip install .
deltabot init rss-bot@mail.example.org password
deltabot serve
```

In this example, the bot would then run under rss-bot@mail.example.org. If you
want to use it, write "/help" to rss-bot@mail.example.org, or whatever mail
address you initialized it with.

You can find other good tips on running bots at
https://bots.delta.chat/howto.html.

