from sqlalchemy import create_engine, Column, Integer, String
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
