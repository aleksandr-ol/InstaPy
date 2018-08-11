from instapy import InstaPy
import traceback
import env
import schedule
import time
from proxy_extension import create_proxy_extension
import random

# bot.set_dont_unfollow_active_users(enabled=True, posts=2)
# bot.set_delimit_commenting(enabled=True, max=32, min=3)
# bot.set_smart_hashtags(['portraitpage', 'portraitgames', 'agameof10k', 'a], limit=3, sort='top', log_tags=True)
# bot.clarifai_check_img_for(['landscape'], comment=True, comments=['Awesome shot!😄', 'Nice shot!😄', 'Great!😄', 'Nice one', 'Awesome', 'Cool!'])
# bot.like_by_locations(['31499759/rome-italy'], amount=10, skip_top_posts=False)
# bot.like_by_feed(amount=20, randomize=True, unfollow=True, interact=True)

dont_like = env.dont_like
ignore_words = env.ignore_words
friend_list = env.friend_list


def routine_follow_unfollow(bot, current_run):
    bot.follow_by_tags([current_run.get("hashtag")], amount=10)
    bot.unfollow_users(
        amount=50,
        InstapyFollowed=(True, "nonfollowers"),
        style="FIFO",
        unfollow_after=6 * 60 * 60,
        sleep_delay=60,
    )
    return True


def routine_likes(bot, current_run):
    bot.set_user_interact(
        amount=random.randint(1, 3), randomize=True, percentage=10, media="Photo"
    )
    bot.like_by_feed(amount=20, randomize=True, unfollow=True, interact=True)
    bot.like_by_tags(
        [current_run.get("hashtag")], amount=30, interact=True, media="Photo"
    )
    return True


current_run = {
    "hashtag": None,
    routine: None,
    "routine_follow_unfollow": routine_follow_unfollow,
    "routine_likes": routine_likes,
}


def job():
    current_run.hashtag = random.choice(env.hashtags)
    bot = InstaPy(
        username=env.username,
        password=env.passsword,
        selenium_local_session=False,
        headless_browser=True,
        bypass_suspicious_attempt=True,
        multi_logs=True,
        proxy_address="212.237.52.87",
        proxy_port=443,
    )
    try:
        bot.set_selenium_remote_session(selenium_url="http://selenium:4444/wd/hub")
        bot.login()
        bot.set_relationship_bounds(
            enabled=True,
            potency_ratio=None,
            delimit_by_numbers=True,
            max_followers=10000,
            max_following=3000,
            min_followers=500,
            min_following=50,
        )
        # bot.set_relationship_bounds(
        #     enabled=True,
        #     # potency_ratio=1.3,
        #     delimit_by_numbers=True,
        #     min_followers=750,
        #     # max_followers=300000,
        #     # max_following=5000,
        #     # min_following=500,
        # )
        # bot.set_delimit_liking(enabled=True, max=None, min=10)
        bot.set_use_clarifai(enabled=True, api_key=env.clarifai_apikey)
        bot.set_dont_include(friend_list)
        bot.set_dont_like(dont_like)
        bot.set_ignore_if_contains(ignore_words)
        bot.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=10, media="Photo"
        )
        bot.set_do_follow(enabled=True, percentage=5, times=1)

        bot.clarifai_check_img_for(env.clarifai_check_img_for)

        routine = None
        if current_run.routine is None:
            routine = current_run.get("routine_likes")
            current_run.routine = "routine_likes"
        elif current_run.routine == "routine_likes":
            routine = current_run.get("routine_follow_unfollow")
            current_run.routine = "routine_follow_unfollow"
        elif current_run.routine == "routine_follow_unfollow":
            routine = current_run.get("routine_likes")
            current_run.routine = "routine_likes"

        routine(bot, current_run)

    except expression as identifier:
        print(traceback.format_exc())
    finally:
        bot.end()


# job()
schedule.every(2).hours.do(job).run()

while True:
    schedule.run_pending()
    time.sleep(1)
