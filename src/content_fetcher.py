import feedparser
import praw
import random
import os
import requests
from typing import List, Dict, Optional

class ContentFetcher:
    def __init__(self, rss_feeds: List[str], reddit_client_id: str, reddit_secret: str, user_agent: str):
        self.rss_feeds = rss_feeds
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_secret,
            user_agent=user_agent
        )

    def fetch_news(self, limit: int = 5) -> List[Dict]:
        articles = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit]:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.summary[:200] + "...",
                        "source": feed.feed.title
                    })
            except Exception as e:
                print(f"Error al leer RSS {feed_url}: {e}")
        return articles

    def fetch_meme(self, subreddits: List[str]) -> Optional[str]:
        subreddit_name = random.choice(subreddits)
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = list(subreddit.hot(limit=50))
        image_posts = [p for p in posts if p.url.endswith(('.jpg', '.png', '.jpeg', '.gif')) and not p.spoiler]
        if not image_posts:
            return None
        post = random.choice(image_posts)
        image_url = post.url
        resp = requests.get(image_url, stream=True)
        if resp.status_code == 200:
            os.makedirs("data/memes", exist_ok=True)
            filename = f"data/memes/{post.id}.{image_url.split('.')[-1]}"
            with open(filename, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            return filename
        return None