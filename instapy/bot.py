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

LIKE_NUMBER = 5, 10
LIKE_FEED_NUMBER = 5, 10
FOLLOW_NUMBER = 5, 10
UNFOLLOW_NUMBER = 5, 10

Proxies = [
    ("151.80.140.233", 54566),
    ("80.211.201.9", 8888),
    ("95.110.224.30", 31275),
    ("95.110.224.30", 31431),
    ("95.110.229.182", 4887),
    ("212.237.52.87", 443),
    ("151.80.140.233", 54566),
    ("212.237.63.84", 8888),
    ("80.211.141.177", 8888),
    ("80.211.141.30", 8888),
    ("80.211.5.160", 8888),
    ("212.237.30.237", 8888),
    ("80.211.148.100", 8888),
    ("80.211.182.207", 8888),
    ("212.237.26.124", 8888),
    ("80.211.184.53", 8888),
    ("80.211.228.238", 8888),
    ("80.211.6.201", 8888),
    ("80.211.148.20", 8888),
    ("212.237.23.60", 2000),
    ("212.237.51.54", 8888),
    ("80.211.157.69", 8888),
    ("80.211.0.244", 8888),
    ("212.237.37.152", 8888),
    ("217.61.15.26", 3128),
    ("80.211.4.187", 8080),
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
        self.setup_worker()
        print("using proxy", self.proxy[0], self.proxy[1])
        super().__init__(
            username=self.account["username"],
            password=self.account["password"],
            selenium_local_session=False,
            headless_browser=True,
            bypass_suspicious_attempt=True,
            multi_logs=True,
            action_logger=self.save_userlog,
            proxy_address=self.proxy[0],
            proxy_port=self.proxy[1],
        )
        # self.fork_controller()
        self.set_bot_status("active")
        self.start_bot_session()

    def setup_worker(self):
        os.environ['TZ'] = 'Europe/Rome'
        time.tzset()
        self.proxy = random.choice(Proxies)

    #  start_bot_session
    def start_bot_session(self):
        try:
            self.pre_login()
            super().login()
            self.post_login()
            self.set_session_settings()
            self.start_routines()
            self.on_session_end()
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
        # self.set_use_clarifai(
        #     enabled=True, api_key=os.getenv('CLARIFAI_APIKEY'))
        # self.clarifai_check_img_for(clarifai_check_img_for)

        if self.account.get("set_relationship_bounds", {}).get('enabled', False):
            # print('setting set_relationship_bounds',
            #       self.account.get("set_relationship_bounds", {}))
            set_relationship_bounds = self.account.get(
                "set_relationship_bounds", {"enabled": False})
            self.set_relationship_bounds(**set_relationship_bounds)

        if len(self.account.get('dont_include', [])):
            # print('setting dont_include', self.account.get('dont_include', []))
            self.set_dont_include(self.account.get("dont_include"))

        if len(self.account.get('dont_like', [])):
            # print('setting dont_like', self.account.get('dont_like', []))
            self.set_dont_like(self.account.get("dont_like"))

        if self.account.get('set_user_interact', None):
            self.set_user_interact(
                amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
            )
        return 0

    def start_routines(self):
        self.on_session_start()
        action_ratio_multiplier = self.account.get(
            'action_ratio_multiplier', 1)

        if self.account.get('hashtag_pointer', None):
            self.like_by_tags(
                [self.account.get('hashtag_pointer')],  # must be array!
                amount=random.randint(*LIKE_NUMBER)*action_ratio_multiplier,
                interact=True,
                media="Photo",
            )

        if self.account.get('like_by_feed', False):
            self.like_by_feed(amount=random.randint(*LIKE_FEED_NUMBER)*action_ratio_multiplier,
                              randomize=True, interact=True)

        if self.account.get('follow_user_followers') and len(self.account.get('follow_user_followers')) > 0:
            self.follow_user_followers(
                self.account.get('follow_user_followers', []),
                randomize=True,
                interact=True,
                amount=random.randint(5, 15)*action_ratio_multiplier,
            )

        if self.account.get('hashtag_pointer', None):
            self.set_relationship_bounds(
                enabled=True, potency_ratio=random.choice([-1.3, 1.3]))
            self.follow_by_tags([self.account.get('hashtag_pointer')],  # must be array!
                                amount=random.randint(*FOLLOW_NUMBER)*action_ratio_multiplier)

        self.unfollow_users(
            amount=random.randint(*UNFOLLOW_NUMBER)*action_ratio_multiplier,
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=48 * 60 * 60,
            sleep_delay=120,
        )

    # refresh data on session start
    def on_session_start(self):
        if (len(self.account.get('hashtags', [])) and self.account.get('hashtag_pointer', None) is None):
            self.account['hashtag_pointer'] = self.account["hashtags"][0]
        return True

    def on_session_end(self):
        print("On session end")
        self.end()
        break_time_in_sec = random.randint(8, 37) * 60  # 5-30 min
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
        current_pointer = self.account.get('hashtag_pointer')
        next_hashtag = None
        if len(hashtags) is 0:
            next_hashtag = None
        elif current_pointer and (current_pointer in hashtags) and hashtags.index(current_pointer) is not len(hashtags) - 1:
            next_index = hashtags.index(current_pointer) + 1
            next_hashtag = hashtags[next_index]
        else:
            next_index = 0
            next_hashtag = hashtags[next_index]
        print("next_hashtag", next_hashtag)
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
            date = now + datetime.timedelta(seconds=int(sec))
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
