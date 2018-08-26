# import lazarus

# lazarus.default()

from instapy import InstaPy
import datetime
import traceback
import env
# import schedule
import time
from proxy_extension import create_proxy_extension
import random
import pymongo


class Bot(InstaPy):
    def __init__(self, *args, **kwards):
        self.connect_mongodb()
        self.user_email = kwards.get("user_email")
        self.user_account = kwards.get("user_account")
        self.current_account = self.get_user_data(
            self.user_email, self.user_account)
        super().__init__(
            username=self.current_account["username"],
            password=self.current_account["password"],
            selenium_local_session=False,
            headless_browser=True,
            bypass_suspicious_attempt=True,
            multi_logs=True,
            # proxy_address="212.237.52.87",
            # proxy_port=443,
        )

    def connect_mongodb(self):
        self.db = pymongo.MongoClient("mongodb", 27017).instapy
        return self.db

    def get_user_data(self, user_email, user_account):
        self.current_user = self.db.user.find_one({"email": user_email})
        if not self.current_user:
            print("User not found, exiting.")
            exit(1)
        current_account = self.db.instagram_account.find_one(
            {"user": self.current_user["_id"], "username": user_account}
        )
        if not current_account:
            print("Acccounts not found, exiting.")
            exit(1)
        print(current_account["username"])
        return current_account

    def save_userlog(self, action="INFO", payload={}):
        user_id = self.current_user.get("_id")
        return self.db.userlog.insert(
            {
                "user": user_id,
                action: action,
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
        else:
            pointer += 1
        current_hashtag = hashtags[pointer: pointer + 1]

        print("Starting with current hashtag %s", (current_hashtag[0]))

        self.set_hashtag_pointer(current_hashtag[0])
        return current_hashtag

    def set_hashtag_pointer(self, hashtag):
        return self.db.instagram_account.update(
            {"user": self.current_user["_id"]}, {
                "$set": {"hashtag_pointer": hashtag}}
        )

    def set_current_settings(self):
        account = self.current_account
        self.set_relationship_bounds(
            enabled=True,
            # potency_ratio=1.3,
            delimit_by_numbers=False,
            max_followers=10000,
            max_following=3000,
            min_followers=400,
            min_following=50,
        )
        self.clarifai_check_img_for(account["clarifai_check_img_for"])
        self.set_dont_include(account["friend_list"])
        self.set_dont_like(account["dont_like"])
        self.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
        )
        return 0

    def set_routines(self):
        account = self.current_account
        self.like_by_tags(
            self.current_hashtag,
            amount=random.randint(5, 15),
            interact=True,
            media="Photo",
        )

        self.like_by_feed(amount=random.randint(5, 10),
                          randomize=True, interact=True)

        self.follow_user_followers(
            account["follow_userbase"],
            randomize=True,
            interact=True,
            amount=random.randint(5, 10),
        )

        self.follow_by_tags(self.current_hashtag, amount=random.randint(5, 25))
        self.unfollow_users(
            amount=random.randint(25, 50),
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=24 * 60 * 60,
            sleep_delay=655,
        )
        self.on_session_end()
        return 0

    def on_session_end(self):
        self.end()
        self.take_a_break(30 * 60)  # 30 min
        self.current_account = self.get_user_data(
            self.user_email, self.user_account)
        return self.login()

    def take_a_break(self, break_time_in_seconds=60):
        return time.sleep(break_time_in_seconds)

    def login(self):
        self.current_hashtag = self.get_current_hashtag()
        self.set_selenium_remote_session(
            selenium_url="http://selenium:4444/wd/hub")
        self.set_current_settings()
        self.set_routines()
        return super().login()


bot = Bot(user_email=env.email, user_account=env.username)
bot.login()
