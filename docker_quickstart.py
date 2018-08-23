from instapy import InstaPy
import traceback
import env
import schedule
import time
from proxy_extension import create_proxy_extension
import random


def job(cursor=0, username=env.username, password=env.password):
    current_hashtag = env.hashtags[cursor : cursor + 1]
    bot = InstaPy(
        username=username,
        password=password,
        selenium_local_session=False,
        headless_browser=True,
        bypass_suspicious_attempt=True,
        multi_logs=True,
    )
    try:
        bot.set_selenium_remote_session(selenium_url="http://selenium:4444/wd/hub")
        bot.login()
        bot.set_relationship_bounds(
            enabled=True,
            # potency_ratio=1.3,
            delimit_by_numbers=True,
            max_followers=10000,
            max_following=3000,
            min_followers=400,
            # min_following=50,
        )

        bot.clarifai_check_img_for(env.clarifai_check_img_for)
        bot.set_dont_include(env.friend_list)
        bot.set_dont_like(env.dont_like)
        bot.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=30, media="Photo"
        )

        bot.like_by_tags(
            current_hashtag, amount=random.randint(5, 15), interact=True, media="Photo"
        )
        bot.like_by_feed(amount=random.randint(5, 10), randomize=True, interact=True)

        bot.follow_user_followers(
            env.follow_userbase,
            randomize=True,
            interact=True,
            amount=random.randint(5, 10),
        )

        bot.follow_by_tags(current_hashtag, amount=random.randint(5, 25))
        bot.unfollow_users(
            amount=random.randint(25, 50),
            InstapyFollowed=(True, "nonfollowers"),
            style="RANDOM",
            unfollow_after=24 * 60 * 60,
            sleep_delay=655,
        )
    except expression as identifier:
        print(traceback.format_exc())
    finally:
        bot.end()
        wait = 60 * 60  # 1hr
        cursor += 1
        if cursor == len(env.hashtags) - 1:
            cursor = 0
            print("rewinding hastags, starting over in 3hrs")
            time.sleep(wait * 3)
        else:
            time.sleep(wait)
        return job(cursor)


job()
