import atexit
import os
from dotenv import load_dotenv

load_dotenv()

from instapy import InstaPy
import datetime
import traceback
import time
import random
# from bson.objectid import ObjectId
from .mongodb import Database
from .bot import Bot
import multiprocessing

MongoDB = Database(
    host=os.getenv("MONGODB_HOST"),
    port=int(os.getenv("MONGODB_PORT")),
    database=os.getenv("MONGODB_DB"),
)

# restart active when main process restart from crash


def stop_all_bot():
    Account = MongoDB.get_collection("instagramAccount")
    Account.update_many({"botStatus": "active"}, {
                        "$set": {"botStatus": "restart"}})
    # if a bot is set as paused but without untild schedule for restart
    # this mainly due to error.
    # Account.update_many({"botStatus": "paused", "$or": [{"pausedUntil": {"$exists": False}}, {"pausedUntil": None}]}, {
    #                     "$set": {"botStatus": "restart"}})


def exit_handler():
    print("Exiting..")
    try:
        stop_all_bot()
    except Exception as error:
        print(str(error))
        pass


atexit.register(exit_handler)
Account = MongoDB.get_collection("instagramAccount")
User = MongoDB.get_collection("users")


def run():
    active_bots = {}
    Bot.on_script_start(MongoDB)
    while True:
        print("[BotsManager]: Looking for stopped account to run...")
        query = {
            "$or": [
                {"botStatus": "stopped"},
                {"botStatus": "restart"},
                {"botStatus": "paused", "pausedUntil": {
                    "$lte": datetime.datetime.now()}},
            ],
            # "expiresOn": {"$lt": datetime.datetime.now()}
        }
        for account in Account.find(query):
            user = User.find_one({"_id": account["user"]})
            if user and account:
                process_name = "%s_%s" % (
                    account.get('_id'), account.get('username'))

                """
                  HANDLE CLIENT CHANGING BOT STATUS TO STOPPED:
                  If account is set to stop and we have one running 
                  stop it
                """
                if account.get('botStatus') == 'stopped' or account.get('botStatus') == 'restart':
                    if active_bots.get(process_name, None):
                        print("found stopped account still working: Exterminate!",
                              account["username"])
                        active_bots.get(process_name).terminate()
                        active_bots.pop(process_name)  # dictionary

                    if account.get('botStatus') == 'stopped':
                        continue  # skip account since is stopped

                account['user'] = user
                print("found inactive account", account.get('username'))
                try:
                    args = {"account": account}
                    process = multiprocessing.Process(
                        target=Bot, kwargs=args)
                    process.name = process_name
                    print(
                        "MULTI - Starting user: %s at %s"
                        % (
                            account["username"],
                            datetime.datetime.now().strftime("%H:%M:%S"),
                        )
                    )
                    active_bots.setdefault(process.name, process)
                    process.start()
                    # process.join()
                    # bot.set_bot_status("active")
                except Exception as error:
                    print("[BotsManager]: Error - ", str(error))
                    # bot.set_bot_status("stopped")

        time.sleep(10)
