from instapy import InstaPy
import env

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder

insta_username = env.insta_username
insta_password = env.insta_password

dont_like = env.dont_like
ignore_words = env.ignore_words
friend_list = env.friend_list

bot = InstaPy(
    username=insta_username,
    password=insta_password,
    selenium_local_session=False,
    headless_browser=True,
)
bot.set_selenium_remote_session(selenium_url="http://selenium:4444/wd/hub")
bot.login()
bot.set_relationship_bounds(
    enabled=True,
    potency_ratio=1.5,
    delimit_by_numbers=True,
    # max_followers=300000,
    min_followers=750,
    # max_following=5000,
    # min_following=500,
)
bot.set_delimit_liking(enabled=True, max=None, min=10)

bot.set_use_clarifai(enabled=True, api_key="fb4a4026cc2947edb7cc8e7ce67dbeca")
bot.set_dont_include(friend_list)
bot.set_dont_like(dont_like)
bot.set_ignore_if_contains(ignore_words)
bot.set_user_interact(amount=3, randomize=True, percentage=100, media="Photo")
bot.like_by_tags(env.like_by_tags, amount=100, interact=True, media="Photo")
session.like_by_feed(amount=100, randomize=True, unfollow=True, interact=True)

# avoid activity on


bot.set_dont_unfollow_active_users(enabled=True, posts=3)

bot.unfollow_users(
    amount=60,
    InstapyFollowed=(True, "nonfollowers"),
    style="FIFO",
    unfollow_after=55 * 60 * 60,
    sleep_delay=501,
)

bot.clarifai_check_img_for(env.clarifai_check_img_for)

bot.end()

