# import lazarus

# lazarus.default()
import atexit
import os
import json
from dotenv import load_dotenv

load_dotenv()

from instapy import InstaPy
import datetime
import traceback
import env

# import schedule
# from proxy_extension import create_proxy_extension
import time
import random
import pymongo
from bson.objectid import ObjectId
from instapy import mongodb
import multiprocessing

MongoDB = mongodb.Database(
    host=os.getenv("MONGODB_HOST"),
    port=int(os.getenv("MONGODB_PORT")),
    database=os.getenv("MONGODB_DB"),
)


class Bot(InstaPy):
    def __init__(self, *args, **kwards):
        self._retry_loggin = 0
        self.connect_mongodb()
        self.set_collection()
        self.account = kwards.get("account")
        self.user = kwards.get("user")
        self.user_email = user["email"]
        self.user_account = account["username"]
        self.current_account = self.get_user_data(
            self.user_email, self.user_account)
        super().__init__(
            username=self.current_account["username"],
            password=self.current_account["password"],
            selenium_local_session=False,
            headless_browser=True,
            bypass_suspicious_attempt=True,
            multi_logs=True,
            action_logger=self.save_userlog
            # proxy_address="212.237.52.87",
            # proxy_port=443,
        )

    # Reconnect to be thread-safe
    def connect_mongodb(self):
        MongoDB = mongodb.Database(
            host=os.getenv("MONGODB_HOST"),
            port=int(os.getenv("MONGODB_PORT")),
            database=os.getenv("MONGODB_DB"),
        )
        self.db_client = MongoDB
        self.db = self.db_client.get_database()
        pass

    def set_collection(self):
        self.User = self.db_client.get_collection("user")
        self.InstagramAccount = self.db_client.get_collection(
            "instagram_account")
        self.ActionLog = self.db_client.get_collection("actionlog")
        return True

    def get_user_data(self, user_email, user_account):

        self.current_user = self.User.find_one({"email": user_email})
        if not self.current_user:
            print("User not found, exiting.")
            exit(1)
        current_account = self.InstagramAccount.find_one(
            {"user": self.current_user["_id"], "username": user_account}
        )
        if not current_account:
            print("Acccounts not found, exiting.")
            exit(1)
        print(current_account["username"])
        return current_account

    def save_userlog(self, action="INFO", payload={}):
        user_id = self.current_user.get("_id")
        account_id = self.current_account.get("_id")
        if (
            self.current_account
            and self.current_account.get("username")
            and not payload.get("username")
        ):
            payload['username'] = self.current_account.get("username")
        return self.ActionLog.insert(
            {
                "user": user_id,
                "account": account_id,
                "action": action,
                "data": payload,
                "createdAt": datetime.datetime.utcnow(),
            }
        )

    def get_current_hashtag(self):
        hashtags = self.current_account.get("hashtags", [])
        pointer = None
        if not len(hashtags):
            return []
        elif not self.current_account.get("hashtag_pointer"):
            pointer = 0
        else:
            pointer = hashtags.index(
                self.current_account.get("hashtag_pointer"))

        # rewind if at last position
        if pointer != 0 and pointer == len(hashtags) - 1:
            pointer = 0
            # if rewinding take a break since we did a pretty long session to get here
            self.take_a_break(random.randint(90, 120) * 60)
        else:
            pointer += 1
        current_hashtag = hashtags[pointer: pointer + 1]

        print("Starting with current: hashtag %s" % (current_hashtag[0]))

        self.set_hashtag_pointer(current_hashtag[0])
        return current_hashtag

    def set_hashtag_pointer(self, hashtag):
        return self.InstagramAccount.update(
            {"user": self.current_user["_id"]}, {
                "$set": {"hashtag_pointer": hashtag}}
        )

    def set_current_settings(self):
        account = self.current_account
        self.set_relationship_bounds(
            enabled=True,
            # potency_ratio=1.21,
            # delimit_by_numbers=True,
            # max_followers=10000,
            # max_following=3000,
            # min_followers=400,
            # min_following=50,
            delimit_by_numbers=True,
            max_followers=4590,
            max_following=5555,
            min_followers=45,
            min_following=77,
        )
        self.clarifai_check_img_for(account["clarifai_check_img_for"])
        self.set_dont_include(account["friend_list"])
        self.set_dont_like(account["dont_like"])
        self.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
        )
        return 0

    def start_routines(self):
        account = self.current_account
        self.like_by_tags(
            self.current_hashtag,
            amount=random.randint(15, 35),
            interact=True,
            media="Photo",
        )

        # self.like_by_feed(amount=random.randint(5, 10), randomize=True, interact=True)

        # Broken
        # self.follow_user_followers(
        #     account["follow_userbase"],
        #     randomize=True,
        #     interact=True,
        #     amount=random.randint(5, 10),
        # )

        self.follow_by_tags(self.current_hashtag,
                            amount=random.randint(10, 25))

        self.unfollow_users(
            amount=random.randint(25, 50),
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=24 * 60 * 60,
            sleep_delay=120,
        )
        self.on_session_end()
        return 0

    def on_session_end(self):
        self.end()
        self.action_logger(
            action="SESSION_END",
            payload={
                "message": "Session ending",
                "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
            },
        )
        self.set_bot_status("paused")
        self.take_a_break(random.randint(5, 30) * 60)  # 30 min
        self.current_account = self.get_user_data(
            self.user_email, self.user_account)
        return self.login()

    def take_a_break(self, break_time_in_seconds=60):
        self.action_logger(
            action="BREAK",
            payload={
                "message": "Taking a break for %s seconds" % (break_time_in_seconds),
                "date": datetime.datetime.fromtimestamp(time.time()).strftime(
                    "%H:%M:%S %d-%m-%Y"
                ),
            },
        )
        return time.sleep(break_time_in_seconds)

    def shoud_sleep_for_the_night(self, active=True):
        if active:
            dt = datetime.datetime.now()
            if dt.hour > 0 and dt.hour < 8:
                # start at 8 but add random on minutes
                dt_hr = 8 - int(dt.hour)
                dt_mt = random.randint(1, 60)
                break_time_in_seconds = (dt_hr * dt_mt) * 60
                # self.logger.info("[%s] Sleeping for the night for %s hour and %s minutes" % (self.current_account.username, dt_hr, dt_mt))
                self.action_logger(
                    action="NIGHT_BREAK",
                    payload={
                        "message": "Sleeping for the night for %s hour and %s minutes"
                        % (dt_hr, dt_mt),
                        "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
                    },
                )
                return time.sleep(break_time_in_seconds)

        return 1

    def set_bot_status(self, status):
        return self.InstagramAccount.update(
            {"_id": self.account["_id"]}, {"$set": {"botStatus": status}}
        )

    def start_bot_session(self):
        try:
            # self.set_bot_status("launching")
            self.shoud_sleep_for_the_night(active=True)
            self.current_hashtag = self.get_current_hashtag()
            self.set_selenium_remote_session(
                selenium_url="http://instapy_d_selenium_1:4444/wd/hub"
            )
            super().login()
            self.set_bot_status("active")
            self.action_logger(
                action="SESSION_START",
                payload={
                    "message": "Session starting",
                    "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
                },
            )
            self.set_current_settings()
            return self.start_routines()
        except Exception as error:
            print(traceback.format_exc())
            self.action_logger(action="ERROR", payload={"message": str(error)})
            if self._retry_loggin < 3:
                self._retry_loggin += 1
                return self.login()
            else:
                self.set_bot_status("stopped")


while True:
    print("BotManager started. Looking for stopped account to run...")
    jobs = []
    query = {
        "$or": [
            {"botStatus": None},
            {"botStatus": {"$exists": False}},
            {"botStatus": "stopped"},
        ]
    }
    Account = MongoDB.get_collection("instagram_account")
    User = MongoDB.get_collection("user")
    for account in Account.find(query):
        user = User.find_one({"_id": account["user"]})
        print("found inactive account", account["username"])
        if user and Account and __name__ == "__main__":
            try:
                bot = Bot(account=account, user=user)
                p = multiprocessing.Process(target=bot.start_bot_session)
                jobs.append(p)
                print(
                    "MULTI - Starting user: %s at %s"
                    % (
                        account["username"],
                        datetime.datetime.now().strftime("%H:%M:%S"),
                    )
                )
                p.start()
                time.sleep(120)
                # no delay cause some instances of chrome to give errors and stop
            except Exception as error:
                print(str(error))
                bot.set_bot_status("stopped")

    time.sleep(10)


def exit_handler():
    print("Exiting..")
    try:
        Account = MongoDB.get_collection("instagram_account")
        Account.update({}, {"$set": "stopped"}, {"multi": True})
    except Exception as error:
        print(str(error))
        pass


atexit.register(exit_handler)
