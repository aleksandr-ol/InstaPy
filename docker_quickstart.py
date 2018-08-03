from instapy import InstaPy
import env
from proxy_extension import create_proxy_extension

proxy = "212.237.52.87:443"
# proxy_chrome_extension = create_proxy_extension(proxy)


dont_like = env.dont_like
ignore_words = env.ignore_words
friend_list = env.friend_list

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
bot.set_selenium_remote_session(selenium_url="http://selenium:4444/wd/hub")
bot.login()
bot.set_relationship_bounds(
    enabled=True,
    potency_ratio=1.3,
    delimit_by_numbers=True,
    min_followers=750,
    # max_followers=300000,
    # max_following=5000,
    # min_following=500,
)
bot.set_delimit_liking(enabled=True, max=None, min=10)
bot.set_dont_include(friend_list)
bot.set_dont_like(dont_like)
bot.set_ignore_if_contains(ignore_words)
# bot.set_user_interact(amount=3, randomize=True, percentage=50, media="Photo")
# bot.set_do_follow(enabled=True, percentage=20, times=1)
bot.set_dont_unfollow_active_users(enabled=True, posts=3)
# bot.set_delimit_commenting(enabled=True, max=32, min=3)
# bot.set_smart_hashtags(['portraitpage', 'portraitgames', 'agameof10k', 'a], limit=3, sort='top', log_tags=True)
# bot.clarifai_check_img_for(['landscape'], comment=True, comments=['Awesome shot!😄', 'Nice shot!😄', 'Great!😄', 'Nice one', 'Awesome', 'Cool!'])
# bot.set_use_clarifai(enabled=True, api_key=env.clarifai_apikey)
bot.clarifai_check_img_for(env.clarifai_check_img_for)
# bot.like_by_locations(['31499759/rome-italy'], amount=10, skip_top_posts=False)
# bot.follow_by_tags(env.like_by_tags, amount=10)
bot.like_by_tags(env.like_by_tags, amount=10, interact=True, media="Photo")
# bot.like_by_feed(amount=50, randomize=True, unfollow=True, interact=True)
bot.unfollow_users(
    amount=1000,
    InstapyFollowed=(True, "nonfollowers"),
    style="FIFO",
    unfollow_after=12 * 60 * 60,
    sleep_delay=501,
)

bot.end()
