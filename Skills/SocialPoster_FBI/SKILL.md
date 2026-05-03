# Social Media Poster - Facebook/Instagram (FBI) Skill

## Purpose
The Social Media Poster FBI skill handles automated posting to Facebook and Instagram, fetches engagement metrics, generates weekly reports, and manages posting failures with automatic retry logic.

## Configuration
The skill requires a configuration file with API credentials and posting parameters:

```json
{
  "facebook": {
    "access_token": "your_facebook_access_token",
    "page_id": "your_facebook_page_id",
    "enabled": true
  },
  "instagram": {
    "access_token": "your_instagram_access_token",
    "account_id": "your_instagram_account_id",
    "enabled": true
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

## Core Functions

### 1. Auto Post Content
- Accepts text, images, and links for posting
- Handles Facebook and Instagram specific formatting
- Schedules posts according to defined schedule

### 2. Engagement Metrics Fetching
- Fetches likes, comments, shares, and reach data
- Stores metrics in structured format
- Triggers alerts for significant changes in engagement

### 3. Weekly Summary Reports
- Aggregates engagement data for the week
- Generates visual reports and insights
- Identifies top-performing content

### 4. Error Handling & Retry Logic
- Handles API errors gracefully
- Implements exponential backoff for retries
- Logs failures for troubleshooting

### 5. Content Management
- Maintains content queue for scheduled posts
- Validates content before posting
- Supports multiple content types