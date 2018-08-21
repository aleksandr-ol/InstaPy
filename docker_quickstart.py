from instapy import InstaPy
import traceback
import env
import schedule
import time
from proxy_extension import create_proxy_extension
import random


# import random
# random.choice(array)

dont_like = env.dont_like
ignore_words = env.ignore_words
friend_list = env.friend_list
hashtags = env.hashtags


def job(cursor=0):
    current_hashtag = hashtags[cursor : cursor + 1]
    bot = InstaPy(
        username=env.username,
        password=env.passsword,
        selenium_local_session=False,
        headless_browser=True,
        bypass_suspicious_attempt=True,
        multi_logs=True,
        # proxy_address="212.237.52.87",
        # proxy_port=443,
    )
    try:
        bot.set_selenium_remote_session(selenium_url="http://selenium:4444/wd/hub")
        bot.login()
        bot.set_relationship_bounds(
            enabled=True,
            potency_ratio=1.3,
            delimit_by_numbers=True,
            max_followers=10000,
            max_following=3000,
            min_followers=500,
            min_following=50,
        )
        # bot.set_delimit_liking(enabled=True, max=None, min=10)
        # bot.set_use_clarifai(enabled=True, api_key=env.clarifai_apikey)
        # bot.set_dont_include(friend_list)
        # bot.set_dont_like(dont_like)
        # bot.set_ignore_if_contains(ignore_words)
        # # bot.set_dont_unfollow_active_users(enabled=True, posts=3)
        # bot.set_user_interact(
        #     amount=random.randint(1, 3), randomize=True, percentage=20, media="Photo"
        # )
        # bot.set_do_follow(enabled=True, percentage=5, times=1)

        # # bot.set_delimit_commenting(enabled=True, max=32, min=3)
        # # bot.set_smart_hashtags(['portraitpage', 'portraitgames', 'agameof10k', 'a], limit=3, sort='top', log_tags=True)
        # # bot.clarifai_check_img_for(['landscape'], comment=True, comments=['Awesome shot!😄', 'Nice shot!😄', 'Great!😄', 'Nice one', 'Awesome', 'Cool!'])
        # # bot.like_by_locations(['31499759/rome-italy'], amount=10, skip_top_posts=False)
        # bot.follow_user_followers(["portraitgames"], amount=10, randomize=False)
        # # bot.follow_by_tags(env.hashtags, amount=10)
        # bot.like_by_feed(amount=50, randomize=True, unfollow=True, interact=True)
        bot.clarifai_check_img_for(env.clarifai_check_img_for)
        bot.set_dont_include(friend_list)
        bot.set_dont_like(dont_like)
        bot.set_ignore_if_contains(ignore_words)
        bot.set_user_interact(
            amount=random.randint(1, 3), randomize=True, percentage=20, media="Photo"
        )
        bot.follow_user_followers(
            ["portraitgames", "portraits_vision", "portraitvision"],
            amount=10,
            randomize=False,
            interact=True,
            sleep_delay=60,
        )
        bot.follow_by_tags(current_hashtag, amount=20)
        bot.like_by_tags(current_hashtag, amount=20, interact=True, media="Photo")
        bot.unfollow_users(
            amount=100,
            InstapyFollowed=(True, "nonfollowers"),
            style="FIFO",
            unfollow_after=12 * 60 * 60,
            sleep_delay=60,
        )
    except expression as identifier:
        print(traceback.format_exc())
    finally:
        bot.end()
        wait = 60 * 60  # 1hr
        cursor += 1
        if cursor == len(hashtags) - 1:
            cursor = 0
            print("rewinding hastags, starting over in 4hrs")
            time.sleep(wait * 4)
        else:
            time.sleep(wait)
        return job(cursor)


job()
# schedule.every(4).hours.do(job).run()

# while True:
#     schedule.run_pending()
#     time.sleep(1)

