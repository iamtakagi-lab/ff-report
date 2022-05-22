import logging
import asyncio
import json
import tweepy
import os
from aiohttp import ClientSession
from discord import AsyncWebhookAdapter, Webhook

TWITTER_CK = os.environ["TWITTER_CK"]
TWITTER_CS = os.environ["TWITTER_CS"]
TWITTER_AT = os.environ["TWITTER_AT"]
TWITTER_ATS = os.environ["TWITTER_ATS"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

auth = tweepy.OAuthHandler(TWITTER_CK, TWITTER_CS)
auth.set_access_token(TWITTER_AT, TWITTER_ATS)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

DATA_DIST = "/data.json"

logger = logging.getLogger("followback")
format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=format)

def signWith(n):
    if n == 0:
        return f"±{n}"
    elif n < 0:
        return n
    elif n > 0:
        return f"+{n}"

async def post_discord_webhook(text):
    async with ClientSession(raise_for_status=True) as session:
        webhook = Webhook.from_url(
            DISCORD_WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))

        await webhook.send(
            content=text
        )

async def handle():
    me = api.me()
    followers_count = me.followers_count
    friends_count = me.friends_count
    with open(DATA_DIST, mode='r', encoding='utf-8') as file:
        prev_data = json.load(file)
    prev_followers_count = prev_data["followers_count"]
    prev_friends_count = prev_data["friends_count"]
    text = f'Followers: {followers_count} ({signWith(followers_count - prev_followers_count)}) Following: {friends_count} ({signWith(friends_count - prev_friends_count)})'
    logger.info(text)
    await post_discord_webhook(text)
    logger.info("保存中...")
    save(followers_count, friends_count)
    logger.info("保存しました")
    

def save(followers_count, friends_count):
    with open(DATA_DIST, mode='w', encoding='utf-8') as file:
            json.dump({
                'followers_count': followers_count,
                'friends_count': friends_count
            }, file, ensure_ascii=False, indent=4
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handle())