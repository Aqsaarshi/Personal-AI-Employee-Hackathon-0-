# Facebook/Instagram Social Poster (FBI) Skill

## Overview
The Social Media Poster FBI skill handles automated posting to Facebook and Instagram, fetches engagement metrics, generates weekly reports, and manages posting failures with automatic retry logic.

## Features
- **Auto Posting**: Automatically post content with text, images, and links to Facebook and Instagram
- **Engagement Tracking**: Fetches likes, comments, shares, reach, and impressions
- **Weekly Reporting**: Generate comprehensive weekly engagement summary reports
- **Retry Logic**: Handles API errors gracefully with exponential backoff retry mechanism
- **Scheduled Posting**: Post content according to configurable schedule
- **Content Queue**: Manage content in a queue for scheduled publishing

## Configuration
The skill uses `config.json` for API credentials and settings:

```json
{
  "facebook": {
    "access_token": "your_facebook_access_token",
    "page_id": "your_facebook_page_id",
    "enabled": false
  },
  "instagram": {
    "access_token": "your_instagram_access_token",
    "account_id": "your_instagram_account_id",
    "enabled": false
  },
  "posting_schedule": {
    "enabled": true,
    "time": "09:00",
    "timezone": "UTC",
    "days": ["mon", "wed", "fri"]
  },
  "retry_settings": {
    "max_attempts": 3,
    "delay_seconds": 60
  },
  "engagement_tracking": {
    "fetch_interval_minutes": 30,
    "metrics": ["likes", "comments", "shares", "reach", "impressions"]
  }
}
```

## Usage Examples

### Basic Usage
```python
from social_poster_fbi import SocialPosterFBI

# Initialize the poster
poster = SocialPosterFBI()

# Post directly to Facebook
result = poster.post_to_facebook(
    "Check out our latest product!",
    "https://example.com/image.jpg",
    "https://example.com/product"
)

# Post directly to Instagram
result = poster.post_to_instagram(
    "New product alert!",
    "https://example.com/image.jpg"
)
```

### Queue Content for Scheduled Posting
```python
# Queue content for scheduled posting
content_id = poster.queue_content({
    "message": "Check out our latest product update!",
    "image_url": "https://example.com/image.jpg",
    "link": "https://example.com/product",
    "platforms": {"facebook": True, "instagram": True}
})

# Process queue according to schedule
poster.process_content_queue()
```

### Fetch Engagement Metrics
```python
# Fetch current engagement metrics
metrics = poster.fetch_engagement_metrics()
print(f"Engagement metrics: {metrics}")
```

### Generate Weekly Summary
```python
# Generate and save weekly summary
summary = poster.generate_weekly_summary()
poster.save_report(summary)
```

## API Integration Templates
The skill provides templates for:
- Facebook Graph API v18.0
- Instagram Graph API v18.0
- Error handling for common API responses
- Rate limit management
- Media upload functionality

## Error Handling & Retry Logic
- Automatic retry with exponential backoff
- Detailed error logging
- Graceful degradation when APIs are unavailable
- Configurable retry attempts and delays

## Weekly Summary Report
The weekly summary includes:
- Total posts across platforms
- Engagement metrics breakdown
- Top performing content
- Average engagement rates
- Comparative analysis with previous periods