import sys
import os
import time
from .mongodb import Database

MongoDB = Database(
    host=os.getenv("MONGODB_HOST"),
    port=int(os.getenv("MONGODB_PORT")),
    database=os.getenv("MONGODB_DB"),
)


def controller(bot=None):
    account = bot.account
    while True:
        Account = MongoDB.get_collection('instagramAccount')
        fetched = Account.find_one({"_id": account.get('_id')})
        if not fetched:
            print("[BotController]: account deleted. stopping activity.")
            return sys.exit(0)

        fetchedBotStatus = fetched.get('botStatus', None)
        if fetchedBotStatus and fetchedBotStatus is not account.get('botStatus', None):
            if fetchedBotStatus == 'stopped' and bot:
                # bot.end()
                return sys.exit(0)

        time.sleep(10)
