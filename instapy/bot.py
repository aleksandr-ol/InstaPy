import sys
import os
from dotenv import load_dotenv
from .mongodb import Database
from instapy import InstaPy
import datetime
import time
import traceback
import random

load_dotenv()
os.environ['TZ'] = 'Europe/Rome'
time.tzset()


class Bot(InstaPy):
    def __init__(self, *args, **kwards):
        self.process = None
        self._retry_loggin = 0
        self.connect_mongodb()
        self.account = kwards.get("account")
        super().__init__(
            username=self.account["username"],
            password=self.account["password"],
            selenium_local_session=False,
            headless_browser=True,
            bypass_suspicious_attempt=True,
            multi_logs=True,
            action_logger=self.save_userlog
            # proxy_address="212.237.52.87",
            # proxy_port=443,
        )
        self.set_bot_status("active")
        self.start_bot_session()
        # no delay cause some instances of chrome to give errors and stop
        # this was after process.start if you encount error after moving it here
        # print("waiting 30 second before starting to be sure chrome is up")
        time.sleep(30)

    #  start_bot_session
    def start_bot_session(self):
        try:
            self.pre_login()
            super().login()
            self.post_login()
            self.set_session_settings()
            self.start_routines()
        except Exception as error:
            print("[Bot]: Error - ", traceback.format_exc())
            self.action_logger(action="ERROR", payload={"message": str(
                error), "stack": str(traceback.format_exc())})
            if self._retry_loggin < 2:
                self._retry_loggin += 1
                return self.start_bot_session()
            else:
                return self.on_session_end()

    def start_routines(self):
        self.on_session_start()

        if self.account.get('hashtag_pointer', None):
            self.like_by_tags(
                self.account.get('hashtag_pointer'),
                amount=random.randint(15, 35),
                interact=True,
                media="Photo",
            )

        # self.like_by_feed(amount=random.randint(5, 10), randomize=True, interact=True)

        # Broken
        # self.follow_user_followers(
        #     self.account["follow_userbase"],
        #     randomize=True,
        #     interact=True,
        #     amount=random.randint(5, 10),
        # )

        if self.account.get('hashtag_pointer', None):
            self.follow_by_tags(self.account.get('hashtag_pointer'),
                                amount=random.randint(10, 25))

        self.unfollow_users(
            amount=random.randint(25, 50),
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=24 * 60 * 60,
            sleep_delay=120,
        )
        self.on_session_end()
        return True

    # refresh data on session start
    def on_session_start(self):
        return True

    def on_session_end(self):
        self.end()
        break_time_in_sec = random.randint(5, 30) * 60  # 5-30 min
        self.set_bot_status("paused", break_time_in_sec)
        self.update_hashtag_pointer()
        return sys.exit(0)

    def pre_login(self):
        self.sleep_if_night(active=True)
        self.set_selenium_remote_session(
            selenium_url="http://selenium:4444/wd/hub")

    def post_login(self):
        pass

    ###############
    #   HELPERS   #
    ###############

    def update_hashtag_pointer(self):
        hashtags = self.account.get("hashtags", [])
        next_index = 0
        if len(hashtags) is 0:
            next_hashtag = None
        elif self.account.get('hashtag_pointer') is not None and hashtags.index(self.account.get('hashtag_pointer')) is not len(hashtags) - 1:
            next_index = hashtags.index(
                self.account.get('hashtag_pointer')) + 1
            next_hashtag = hashtags[next_index]

        return self.InstagramAccount.update({"_id": self.account.get('_id', None)}, {"$set": {"hashtag_pointer": next_hashtag}})

    # Run BEFORE running the script
    # For everything to do before starting ALL bot

    @staticmethod
    def on_script_start(MongoDB):
        # set bot stuck on active when bot crashed to make them
        # reinitialize
        Instagram = MongoDB.get_collection("instagram_account")
        try:
            Instagram.update_many({"botStatus": "active"}, {
                "$set": {"botStatus": "restart"}})
        except Exception as error:
            print(error)

    # Run AFTER running the script
    # For everything to do before stopping ALL bot
    @staticmethod
    def on_script_end():
        pass

    # Reconnect to be thread-safe
    def connect_mongodb(self):
        MongoDB = Database(
            host=os.getenv("MONGODB_HOST"),
            port=int(os.getenv("MONGODB_PORT")),
            database=os.getenv("MONGODB_DB"),
        )
        self.db_client = MongoDB
        self.db = self.db_client.get_database()
        self.set_db_models()

    def set_db_models(self):
        self.User = self.db_client.get_collection("user")
        self.InstagramAccount = self.db_client.get_collection(
            "instagram_account")
        self.ActionLog = self.db_client.get_collection("actionlog")
        return True

    def save_userlog(self, action="INFO", payload={}):
        user_id = self.account.get('user', {}).get("_id")
        account_id = self.account.get("_id")
        return self.ActionLog.insert(
            {
                "user": user_id,
                "account": account_id,
                "action": action,
                "data": payload,
                "createdAt": datetime.datetime.utcnow(),
            }
        )

    def set_next_hashtag_pointer(self, hashtag):
        return self.InstagramAccount.update(
            {"_id": self.account["_id"]}, {
                "$set": {"hashtag_pointer": hashtag}}
        )

    def set_session_settings(self):
        if self.account.get("set_relationship_bounds", {}).get('enabled', False):
            set_relationship_bounds = self.account.get(
                "set_relationship_bounds", {})
            self.set_relationship_bounds(
                **set_relationship_bounds
                # enabled=True,
                # potency_ratio=-1.21,
                # delimit_by_numbers=True,
                # # max_followers=10000,
                # # max_following=5555,
                # min_followers=500,
                # # min_following=150,
            )
            pass
        self.clarifai_check_img_for(self.account["clarifai_check_img_for"])
        self.set_dont_include(self.account["friend_list"])
        self.set_dont_like(self.account["dont_like"])
        self.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
        )
        return 0

    def sleep_if_night(self, active=True):
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

                return self.set_bot_status('paused', break_time_in_seconds)

    def set_bot_status(self, status, break_time_in_sec=300):
        """ set bot status in DB
            active|paused|stopped
            active: is running
            paused: bot paused until next run shown in pausedUntil
            stopped: stopped undefinately prob due to error
        """
        def calculate_break_time(sec=300):
            now = datetime.datetime.now()
            date = now + datetime.timedelta(seconds=sec)
            return now, sec, date

        updateObj = {"botStatus": status}
        if status == 'paused':
            now, sec, break_until = calculate_break_time(
                break_time_in_sec)
            updateObj['pausedUntil'] = break_until
        else:
            updateObj['pausedUntil'] = None

        self.InstagramAccount.update(
            {"_id": self.account.get('_id')}, {"$set": updateObj}
        )
        self.action_logger(
            action="SESSION_%s" % (status.upper()),
            payload={
                "message": "Session %s" % (status.upper()),
                "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
            },
        )
        print(">", updateObj)
        if status == 'paused' or status == 'stopped':
            return sys.exit(0)
