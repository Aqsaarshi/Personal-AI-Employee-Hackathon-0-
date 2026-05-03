"""
Social Media Poster - Twitter/X
Handles auto posting tweets, engagement tracking, and reporting
"""
import json
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialPosterTwitter:
    def __init__(self, config_path: str = "Skills/SocialPoster_Twitter/config.json"):
        """Initialize the Twitter Social Media Poster with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # API endpoints
        self.api_base_url = "https://api.twitter.com/2"
        self.upload_base_url = "https://upload.twitter.com/1.1"

        # Initialize engagement tracking
        self.engagement_data = {}
        self.content_queue = []

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "twitter": {
                "api_key": "your_twitter_api_key",
                "api_secret": "your_twitter_api_secret",
                "access_token": "your_twitter_access_token",
                "access_token_secret": "your_twitter_access_token_secret",
                "bearer_token": "your_twitter_bearer_token",
                "enabled": False
            },
            "posting_schedule": {
                "enabled": True,
                "time": "10:00",
                "timezone": "UTC",
                "days": ["tue", "thu", "sat"]
            },
            "retry_settings": {
                "max_attempts": 3,
                "delay_seconds": 60
            },
            "engagement_tracking": {
                "fetch_interval_minutes": 30,
                "metrics": ["likes", "retweets", "replies", "quotes", "impressions"]
            }
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_path}")
            return default_config

    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for Twitter API v2."""
        return {
            "Authorization": f"Bearer {self.config['twitter']['bearer_token']}",
            "Content-Type": "application/json"
        }

    def post_tweet(self, text: str, media_ids: List[str] = None) -> Dict:
        """Post a tweet to Twitter/X."""
        if not self.config["twitter"]["enabled"]:
            logger.warning("Twitter posting is disabled in config")
            return {"success": False, "error": "Twitter posting disabled"}

        # Check character limit
        if len(text) > 280:
            logger.warning(f"Tweet exceeds 280 character limit: {len(text)} chars")
            # Truncate text if necessary (in a real implementation, you'd want to do this more gracefully)
            text = text[:277] + "..."

        # Build the tweet data
        tweet_data = {
            "text": text
        }

        if media_ids:
            tweet_data["media"] = {"media_ids": media_ids}

        # Make the API call
        url = f"{self.api_base_url}/tweets"

        try:
            response = self._make_api_request_with_retry(
                "POST",
                url,
                data=json.dumps(tweet_data),
                headers=self._get_auth_headers()
            )

            if response.get("success"):
                logger.info(f"Successfully posted tweet: {response['data']}")
                return response
            else:
                logger.error(f"Failed to post tweet: {response.get('error', 'Unknown error')}")
                return response

        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {"success": False, "error": str(e)}

    def _upload_media(self, media_url: str) -> Optional[str]:
        """Upload media to Twitter/X."""
        if not media_url:
            return None

        # First, download the media locally (in a real implementation, you'd handle this differently)
        try:
            response = requests.get(media_url)
            if response.status_code != 200:
                logger.error(f"Failed to download media from {media_url}")
                return None

            # For simplicity in this implementation, we won't actually upload media
            # In a real implementation, you'd need to:
            # 1. Download the media file
            # 2. Upload it using Twitter's media upload API
            # 3. Get the media ID to include with your tweet
            logger.info(f"Would upload media from {media_url}")
            return "mock_media_id"  # Placeholder
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            return None

    def _make_api_request_with_retry(self, method: str, url: str, data: str = None, headers: Dict = None, max_retries: int = None) -> Dict:
        """Make an API request with retry logic."""
        if max_retries is None:
            max_retries = self.config["retry_settings"]["max_attempts"]

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = requests.post(url, data=data, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # For Twitter API, even error responses are JSON
                try:
                    result = response.json()
                except:
                    # If response isn't JSON, return as text
                    return {"success": True, "data": response.text}

                # Check response status
                if response.status_code in [200, 201]:
                    return {"success": True, "data": result}
                elif response.status_code == 429:  # Rate limit
                    # Rate limited - wait longer and try again
                    logger.warning(f"Rate limited by Twitter API (attempt {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        # Use rate limit reset time if available
                        delay = self.config["retry_settings"]["delay_seconds"] * (3 ** attempt)  # More aggressive backoff for rate limits
                        time.sleep(delay)
                        continue
                    else:
                        return {"success": False, "error": f"Rate limited: {result.get('detail', 'Rate limit exceeded')}"}
                else:
                    error_msg = result.get('detail', result.get('error', f"HTTP {response.status_code}"))
                    return {"success": False, "error": error_msg}

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries + 1}): {last_error}")

                if attempt < max_retries:
                    # Wait before retrying (exponential backoff)
                    delay = self.config["retry_settings"]["delay_seconds"] * (2 ** attempt)
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    logger.error(f"All retry attempts failed. Last error: {last_error}")
                    return {"success": False, "error": last_error}

            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error making API request: {last_error}")
                return {"success": False, "error": last_error}

        # This line should not be reached, but just in case
        return {"success": False, "error": f"Failed after {max_retries} attempts. Last error: {last_error}"}

    def fetch_engagement_metrics(self, tweet_ids: List[str] = None) -> Dict:
        """Fetch engagement metrics for tweets."""
        metrics = {"tweets": [], "timestamp": datetime.now().isoformat()}

        # If no specific tweet IDs provided, we would normally fetch recent tweets
        # For this implementation, we'll just simulate metrics
        if not tweet_ids:
            # In a real implementation, fetch recent tweet IDs from stored data
            tweet_ids = ["mock_tweet_1", "mock_tweet_2", "mock_tweet_3"]

        # Simulate fetching engagement metrics
        for tweet_id in tweet_ids:
            tweet_metrics = {
                "id": tweet_id,
                "engagement": {
                    "likes": self._generate_mock_metric(10, 1000),
                    "retweets": self._generate_mock_metric(5, 500),
                    "replies": self._generate_mock_metric(2, 100),
                    "quotes": self._generate_mock_metric(1, 50),
                    "impressions": self._generate_mock_metric(100, 50000)
                },
                "timestamp": datetime.now().isoformat()
            }
            metrics["tweets"].append(tweet_metrics)

        # Store for reporting
        self.engagement_data[metrics["timestamp"]] = metrics

        return metrics

    def _generate_mock_metric(self, base: int, max_val: int) -> int:
        """Generate a mock metric value (in real implementation, this would come from the API)."""
        import random
        return random.randint(base, min(base * 10, max_val))

    def generate_weekly_summary(self) -> Dict:
        """Generate a weekly engagement summary report for Twitter."""
        # Get metrics from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_metrics = {
            timestamp: data
            for timestamp, data in self.engagement_data.items()
            if datetime.fromisoformat(timestamp.replace('Z', '+00:00')) >= week_ago
        }

        # Calculate summary statistics
        summary = {
            "period_start": (datetime.now() - timedelta(days=7)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "total_tweets": 0,
            "twitter": {
                "total_engagement": 0,
                "average_engagement": 0,
                "top_performers": [],
                "engagement_breakdown": {
                    "likes": 0,
                    "retweets": 0,
                    "replies": 0,
                    "quotes": 0,
                    "impressions": 0
                }
            }
        }

        # Process collected metrics
        if recent_metrics:
            total_engagement = 0
            engagement_counts = {"likes": 0, "retweets": 0, "replies": 0, "quotes": 0, "impressions": 0}
            all_tweets = []

            for timestamp, metrics in recent_metrics.items():
                for tweet_data in metrics.get("tweets", []):
                    tweet_engagement = tweet_data["engagement"]
                    tweet_total = sum(tweet_engagement.values())
                    total_engagement += tweet_total

                    for metric, value in tweet_engagement.items():
                        engagement_counts[metric] += value

                    # Track tweet for potential top performer
                    all_tweets.append({
                        "id": tweet_data["id"],
                        "total_engagement": tweet_total,
                        "engagement": tweet_engagement,
                        "timestamp": tweet_data["timestamp"]
                    })

            summary["total_tweets"] = len(all_tweets)
            summary["twitter"]["total_engagement"] = total_engagement

            if len(all_tweets) > 0:
                summary["twitter"]["average_engagement"] = total_engagement / len(all_tweets)
                # Sort by total engagement to find top performers
                sorted_tweets = sorted(all_tweets, key=lambda x: x["total_engagement"], reverse=True)
                summary["twitter"]["top_performers"] = sorted_tweets[:3]  # Top 3

            summary["twitter"]["engagement_breakdown"] = engagement_counts

        return summary

    def queue_tweet(self, text: str, media_url: str = None) -> str:
        """Queue a tweet for scheduled posting."""
        tweet_id = f"tweet_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.content_queue)}"

        tweet_data = {
            "id": tweet_id,
            "text": text,
            "media_url": media_url,
            "scheduled_at": datetime.now().isoformat(),
            "status": "queued"
        }

        self.content_queue.append(tweet_data)
        logger.info(f"Queued tweet with ID: {tweet_id}")

        return tweet_id

    def process_tweet_queue(self):
        """Process the tweet queue according to schedule."""
        if not self.config["posting_schedule"]["enabled"]:
            logger.info("Tweet queue processing is disabled")
            return

        # Check if current time matches schedule
        current_time = datetime.now()
        current_day = current_time.strftime("%a").lower()[:3]  # mon, tue, etc.
        current_hour_min = current_time.strftime("%H:%M")

        schedule_days = self.config["posting_schedule"]["days"]
        schedule_time = self.config["posting_schedule"]["time"]

        if current_day in schedule_days and current_hour_min == schedule_time:
            logger.info(f"Processing tweet queue for scheduled time: {current_day} {current_hour_min}")

            # Process queue (in real implementation, you'd have more sophisticated scheduling)
            processed = 0
            for tweet in self.content_queue[:]:  # Copy to avoid modification during iteration
                # Upload media if provided
                media_id = None
                if tweet.get("media_url"):
                    media_id = self._upload_media(tweet["media_url"])

                # Post the tweet
                media_ids = [media_id] if media_id else None
                result = self.post_tweet(tweet["text"], media_ids)

                if result.get("success"):
                    logger.info(f"Successfully processed queued tweet: {tweet['id']}")
                    self.content_queue.remove(tweet)
                    processed += 1
                else:
                    logger.warning(f"Failed to process queued tweet: {tweet['id']} - {result.get('error')}")

                # Be respectful of rate limits
                time.sleep(2)
        else:
            logger.debug(f"Not scheduled time. Current: {current_day} {current_hour_min}, Scheduled: {schedule_days} {schedule_time}")

    def save_report(self, report_data: Dict, filename: str = None):
        """Save the engagement report to a file."""
        if not filename:
            filename = f"twitter_weekly_summary_{datetime.now().strftime('%Y%m%d')}.json"

        reports_dir = Path("Reports")
        reports_dir.mkdir(exist_ok=True)

        filepath = reports_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Saved Twitter report to {filepath}")
        return str(filepath)

# Example usage
if __name__ == "__main__":
    # Initialize the Twitter Poster
    twitter_poster = SocialPosterTwitter()

    # Example: Queue a tweet for posting
    tweet_id = twitter_poster.queue_tweet(
        "Just implemented automated social media posting with @ClaudeAI! 🚀 #AI #Automation",
        "https://example.com/image.jpg"
    )
    print(f"Queued tweet with ID: {tweet_id}")

    # Example: Post a tweet now (not using queue)
    print("\nPosting to Twitter/X...")
    tweet_result = twitter_poster.post_tweet(
        "This is an automated test tweet from our AI assistant! 🤖"
    )
    print(f"Twitter post result: {tweet_result}")

    # Example: Fetch and display engagement metrics (simulated)
    print("\nFetching engagement metrics...")
    metrics = twitter_poster.fetch_engagement_metrics()
    print(f"Engagement metrics: {json.dumps(metrics, indent=2)}")

    # Example: Generate and save weekly summary
    print("\nGenerating weekly summary...")
    summary = twitter_poster.generate_weekly_summary()
    print(f"Weekly summary: {json.dumps(summary, indent=2)}")

    report_path = twitter_poster.save_report(summary)
    print(f"Twitter report saved to: {report_path}")