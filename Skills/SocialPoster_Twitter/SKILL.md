# Social Media Poster - Twitter/X Skill

## Purpose
The Social Media Poster Twitter skill handles automated posting to Twitter/X, fetches engagement metrics, generates weekly reports, and manages posting failures with automatic retry logic.

## Configuration
The skill requires a configuration file with API credentials and posting parameters:

```json
{
  "twitter": {
    "api_key": "your_twitter_api_key",
    "api_secret": "your_twitter_api_secret",
    "access_token": "your_twitter_access_token",
    "access_token_secret": "your_twitter_access_token_secret",
    "bearer_token": "your_twitter_bearer_token",
    "enabled": true
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

## Core Functions

### 1. Auto Post Tweets
- Accepts text content for posting
- Handles Twitter/X specific formatting and character limits
- Schedules tweets according to defined schedule

### 2. Engagement Metrics Fetching
- Fetches likes, retweets, replies, and quote tweets
- Stores metrics in structured format
- Triggers alerts for significant changes in engagement

### 3. Weekly Summary Reports
- Aggregates engagement data for the week
- Generates visual reports and insights
- Identifies top-performing tweets

### 4. Error Handling & Retry Logic
- Handles API errors gracefully
- Implements exponential backoff for retries
- Logs failures for troubleshooting

### 5. Content Management
- Maintains content queue for scheduled tweets
- Validates content before posting
- Checks character limits and formatting