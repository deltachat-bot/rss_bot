from sqlalchemy import create_engine, Column, Integer, String, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    addr = Column(String)
    url = Column(String)
    modified = Column(String)


def engine():
    return create_engine('sqlite:///rss_bot.sqlite', echo=True)


Base.metadata.create_all(engine())
Session = sessionmaker(bind=engine())


def db_subscribe(url, addr, modified):
    session = Session()
    session.add(Subscriptions(addr=addr, url=url, modified=modified))
    session.commit()


def db_unsubscribe(url, addr):
    subscriptions_table = Subscriptions()
    # throws AttributeError: 'Subscriptions' object has no attribute 'delete'
    subscriptions_table.delete().where(and_(Subscriptions.addr == addr, Subscriptions.url == url)).execute()


if __name__ == "__main__":
    print("unsubscribing:")
    addr = "compl4xx@testrun.org"
    url = "https://delta.chat/feed.xml"
    db_unsubscribe(url, addr)