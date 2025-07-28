"""Reddit bot to reply to specific comments.

This script uses the Python Reddit API Wrapper (PRAW) to monitor a subreddit (or
multiple subreddits) for new comments that match a specific phrase and reply
with a predefined response. The behaviour is similar to the "call and
response" pattern described in the official PRAW documentation, where a stream
is used to monitor new comments and a simple conditional triggers a reply.

Before running this script, you need to create a Reddit application and obtain
the credentials (`client_id`, `client_secret`, `username`, and `password`).
PRAW’s `Reddit` class requires a `user_agent` string that identifies your
bot and includes contact information. According to the PRAW documentation,
`subreddit.stream.comments()` yields new comments as they are created and
accepts a `skip_existing` argument to start the stream with only future
comments【949604583635277†L220-L236】. This is important to prevent your bot
from responding to old comments when it first starts.

Fill in the placeholders below with your own credentials, or configure a
``praw.ini`` file as described in the PRAW docs. Keep these values secret!

Usage:
    1. Install PRAW: ``pip install praw``
    2. Edit the credentials below or set up ``praw.ini``.
    3. Optionally adjust ``SUBREDDITS`` to target specific subreddits. Use
       ``"all"`` to monitor all of Reddit.
    4. Run the script: ``python reddit_bot.py``
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Iterable

import praw

# Configure logging to standard output
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def create_reddit_instance() -> praw.Reddit:
    """Create and return a configured Reddit instance.

    Replace the placeholder strings with your bot's credentials. See the PRAW
    documentation for details on authentication. You can also provide these
    values via a ``praw.ini`` file instead of hard‑coding them here.
    """
    return praw.Reddit(
        client_id="YOUR_CLIENT_ID",  # replace with your client ID
        client_secret="YOUR_CLIENT_SECRET",  # replace with your client secret
        username="YOUR_USERNAME",  # replace with your bot's username
        password="YOUR_PASSWORD",  # replace with your bot's password
        user_agent=(
            "new-response-bot v1.0 (by u/YOUR_USERNAME) "
            "— monitors comments for 'New response just dropped' and replies"
        ),
    )


def monitor_comments(
    reddit: praw.Reddit,
    subreddits: Iterable[str],
    trigger_phrase: str,
    reply_text: str,
) -> None:
    """Monitor specified subreddits and reply to comments matching a phrase.

    Parameters
    ----------
    reddit : praw.Reddit
        A configured Reddit instance.
    subreddits : Iterable[str]
        Names of subreddits to monitor. Use ["all"] to monitor all of Reddit.
        PRAW will combine multiple names into a single multireddit if provided.
    trigger_phrase : str
        The exact text (case‑insensitive) that should trigger a reply. Leading
        and trailing whitespace are ignored.
    reply_text : str
        The text that the bot will reply with.

    This function uses the streaming interface described in the PRAW
    documentation to yield new comments from the specified subreddit(s)
    【949604583635277†L220-L236】. It compares each comment’s body to
    ``trigger_phrase``, and if they match exactly (ignoring case and
    whitespace), replies with ``reply_text``.
    """
    # Build the subreddit path. Joining names with "+" allows monitoring
    # multiple subreddits at once (e.g. "test+learnpython").
    subreddit_path = "+".join(subreddits)
    subreddit = reddit.subreddit(subreddit_path)

    # Precompute the lowercase trigger phrase for comparison
    trigger_normalized = trigger_phrase.strip().lower()

    logging.info(
        "Starting comment stream for r/%s; trigger phrase='%s'", subreddit_path, trigger_phrase
    )

    # Use skip_existing=True so the bot only reacts to future comments.
    # Without this, PRAW will emit up to 100 historical comments on start.
    for comment in subreddit.stream.comments(skip_existing=True):
        # Skip comments authored by the bot itself to avoid self‑reply loops.
        try:
            me = reddit.user.me()
            if comment.author and comment.author.name == me.name:
                continue
        except Exception:
            # If we fail to retrieve our own user (rare), just continue.
            pass

        # Compare the normalized body to the trigger phrase
        body_normalized = comment.body.strip().lower()
        if body_normalized == trigger_normalized:
            try:
                logging.info(
                    "Replying to comment id=%s in r/%s", comment.id, comment.subreddit.display_name
                )
                comment.reply(reply_text)
                # Optional: sleep briefly to respect API rate limits
                time.sleep(2)
            except Exception as e:
                logging.error("Failed to reply to comment %s: %s", comment.id, e)
                # To avoid a tight error loop, pause briefly before continuing
                time.sleep(5)


def main(argv: list[str] | None = None) -> int:
    """Entry point of the script.

    This function parses command‑line arguments (if any) and starts the
    monitoring loop. Modify the list of subreddit names or the trigger phrase
    as necessary.
    """
    # Create the Reddit instance
    reddit = create_reddit_instance()

    # Define which subreddits to monitor. Using ["all"] will monitor all of
    # Reddit. For a specific subreddit (e.g. "chess"), change this list.
    SUBREDDITS = ["all"]

    # Define the trigger phrase and the reply text
    TRIGGER_PHRASE = "New response just dropped"
    REPLY_TEXT = "Actual Zombie"

    # Start monitoring comments
    monitor_comments(reddit, SUBREDDITS, TRIGGER_PHRASE, REPLY_TEXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))