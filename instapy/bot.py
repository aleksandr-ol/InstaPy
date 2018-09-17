import sys
import os
from dotenv import load_dotenv
from .mongodb import Database
# from .bot_controller import controller as BotController
from instapy import InstaPy
import datetime
import time
import traceback
import random
import multiprocessing

load_dotenv()
os.environ['TZ'] = 'Europe/Rome'
time.tzset()

clarifai_check_img_for = [
    "nsfw",
    "kid",
    "child",
    "children",
    "teen",
    "food",
    "dog",
    "pet",
    "cat",
    "advertisement",
    "adv",
    "text",
    "low quality",
    "fashion",
    "men",
    "man",
    "china",
    "chinese",
    "arab",
    "male",
    "man",
]


class Bot(InstaPy):
    def __init__(self, *args, **kwards):
        # no delay cause some instances of chrome to give errors and stop
        # this was after process.start if you encount error after moving it here
        # print("waiting 30 second before starting to be sure chrome is up")
        # time.sleep(30)
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
            action_logger=self.save_userlog,
            # proxy_address="212.237.52.87",
            # proxy_port=443,
        )
        # self.fork_controller()
        self.set_bot_status("active")
        self.start_bot_session()

    # def fork_controller(self):
    #     print("fork_controller")
    #     process = multiprocessing.Process(
    #         target=BotController, kwargs={"bot": self})
    #     process.start()

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

    def set_session_settings(self):
        self.set_use_clarifai(
            enabled=True, api_key=os.getenv('CLARIFAI_APIKEY'))
        self.clarifai_check_img_for(clarifai_check_img_for)

        if self.account.get("set_relationship_bounds", {}).get('enabled', False):
            print('setting set_relationship_bounds',
                  self.account.get("set_relationship_bounds", {}))
            set_relationship_bounds = self.account.get(
                "set_relationship_bounds", {"enabled": False})
            self.set_relationship_bounds(**set_relationship_bounds)

        if len(self.account.get('dont_include', [])):
            print('setting dont_include', self.account.get('dont_include', []))
            self.set_dont_include(self.account.get("dont_include"))

        if len(self.account.get('dont_like', [])):
            print('setting dont_like', self.account.get('dont_like', []))
            self.set_dont_like(self.account.get("dont_like"))

        if self.account.get('set_user_interact', None):
            self.set_user_interact(
                amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
            )
        return 0

    def start_routines(self):
        self.on_session_start()
        if self.account.get('hashtag_pointer', None):
            self.like_by_tags(
                [self.account.get('hashtag_pointer')],  # must be array!
                amount=random.randint(15, 25),
                interact=True,
                media="Photo",
            )

        if self.account.get('like_by_feed', False):
            self.like_by_feed(amount=random.randint(15, 20),
                              randomize=True, interact=True)

        # Broken
        # if self.account.get('follow_user_followers', None):
        #     self.follow_user_followers(
        #         self.account["follow_userbase"],
        #         randomize=True,
        #         interact=True,
        #         amount=random.randint(15, 30),
        #     )

        if self.account.get('hashtag_pointer', None):
            self.set_relationship_bounds(
                enabled=True, potency_ratio=random.choice([-1.3, 1.3]))
            self.follow_by_tags([self.account.get('hashtag_pointer')],  # must be array!
                                amount=random.randint(15, 25))

        self.unfollow_users(
            amount=random.randint(25, 50),
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=48 * 60 * 60,
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
        self.update_hashtag_pointer()
        self.set_bot_status("paused", break_time_in_sec)
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

        try:
            return self.InstagramAccount.update({"_id": self.account.get('_id', None)}, {
                "$set": {"hashtag_pointer": next_hashtag}})
        except Exception as error:
            print("update hashtag error", error)

    # Run BEFORE running the script
    # For everything to do before starting ALL bot

    @staticmethod
    def on_script_start(MongoDB):
        # set bot stuck on active when bot crashed to make them
        # reinitialize
        Instagram = MongoDB.get_collection("instagramAccount")
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
        self.User = self.db_client.get_collection("users")
        self.InstagramAccount = self.db_client.get_collection(
            "instagramAccount")
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
        if status == 'paused' or status == 'stopped':
            return sys.exit(0)
