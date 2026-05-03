# Twitter/X Social Poster Skill

## Overview
The Social Media Poster Twitter skill handles automated posting to Twitter/X, fetches engagement metrics, generates weekly reports, and manages posting failures with automatic retry logic.

## Features
- **Auto Tweet Posting**: Automatically post tweets with text content
- **Engagement Tracking**: Fetches likes, retweets, replies, quote tweets, and impressions
- **Weekly Reporting**: Generate comprehensive weekly engagement summary reports
- **Error Handling**: Handles API errors gracefully with exponential backoff retry mechanism
- **Scheduled Posting**: Post tweets according to configurable schedule
- **Content Queue**: Manage tweet content in a queue for scheduled publishing

## Configuration
The skill uses `config.json` for API credentials and settings:

```json
{
  "twitter": {
    "api_key": "your_twitter_api_key",
    "api_secret": "your_twitter_api_secret",
    "access_token": "your_twitter_access_token",
    "access_token_secret": "your_twitter_access_token_secret",
    "bearer_token": "your_twitter_bearer_token",
    "enabled": false
  },
  "posting_schedule": {
    "enabled": true,
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
```

## Usage Examples

### Basic Usage
```python
from social_poster_twitter import SocialPosterTwitter

# Initialize the poster
twitter_poster = SocialPosterTwitter()

# Post a tweet directly
result = twitter_poster.post_tweet("This is an automated tweet from our AI assistant! 🤖")
print(f"Tweet result: {result}")
```

### Queue Tweet for Scheduled Posting
```python
# Queue a tweet for scheduled posting
tweet_id = twitter_poster.queue_tweet(
    "Just implemented automated social media posting with @ClaudeAI! 🚀 #AI #Automation"
)

# Process tweet queue according to schedule
twitter_poster.process_tweet_queue()
```

### Fetch Engagement Metrics
```python
# Fetch engagement metrics for specific tweets
metrics = twitter_poster.fetch_engagement_metrics(["tweet_id_1", "tweet_id_2"])
print(f"Engagement metrics: {metrics}")

# Fetch metrics for recent tweets
metrics = twitter_poster.fetch_engagement_metrics()  # Uses internal tracking
```

### Generate Weekly Summary
```python
# Generate and save weekly summary
summary = twitter_poster.generate_weekly_summary()
twitter_poster.save_report(summary)
```

## API Integration Templates
The skill provides templates for:
- Twitter API v2 endpoints
- Authentication using Bearer tokens
- Error handling for common API responses
- Rate limit management
- Tweet posting functionality

## Error Handling & Retry Logic
- Automatic retry with exponential backoff
- Special handling for rate limits (HTTP 429)
- Detailed error logging
- Graceful degradation when APIs are unavailable
- Configurable retry attempts and delays

## Weekly Summary Report
The weekly summary includes:
- Total tweets posted
- Engagement metrics breakdown (likes, retweets, replies, quotes, impressions)
- Top performing tweets
- Average engagement rates
- Comparative analysis with previous periods
- Engagement per tweet analysis

## Character Limit Handling
- Automatic truncation of tweets exceeding 280 characters
- Warning logs when content exceeds limits
- In a production environment, you'd implement more sophisticated text processing