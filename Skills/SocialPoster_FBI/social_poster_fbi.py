"""
Social Media Poster - Facebook/Instagram (FBI)
Handles auto posting, engagement tracking, and reporting
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

class SocialPosterFBI:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Social Media Poster with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # API endpoints
        self.facebook_base_url = "https://graph.facebook.com/v18.0"
        self.instagram_base_url = "https://graph.facebook.com/v18.0"

        # Initialize engagement tracking
        self.engagement_data = {}
        self.content_queue = []

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "facebook": {
                "access_token": "your_facebook_access_token",
                "page_id": "your_facebook_page_id",
                "enabled": False
            },
            "instagram": {
                "access_token": "your_instagram_access_token",
                "account_id": "your_instagram_account_id",
                "enabled": False
            },
            "posting_schedule": {
                "enabled": True,
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

    def post_to_facebook(self, message: str, image_url: Optional[str] = None, link: Optional[str] = None) -> Dict:
        """Post content to Facebook page."""
        if not self.config["facebook"]["enabled"]:
            logger.warning("Facebook posting is disabled in config")
            return {"success": False, "error": "Facebook posting disabled"}

        access_token = self.config["facebook"]["access_token"]
        page_id = self.config["facebook"]["page_id"]

        # Build the post data
        post_data = {
            "message": message,
            "access_token": access_token
        }

        if link:
            post_data["link"] = link

        # Post with image if provided
        if image_url:
            # First upload the image
            image_upload_url = f"{self.facebook_base_url}/{page_id}/photos"
            image_data = {
                "url": image_url,
                "access_token": access_token,
                "published": False  # Don't publish yet, we'll attach to post
            }

            try:
                image_response = self._make_api_request_with_retry(
                    "POST",
                    image_upload_url,
                    data=image_data
                )

                if image_response.get("success") and "id" in image_response["data"]:
                    # Now create the post with the uploaded image
                    post_data["attached_media[0]"] = json.dumps({"media_fbid": image_response["data"]["id"]})
            except Exception as e:
                logger.error(f"Error uploading image to Facebook: {str(e)}")
                # Continue without image if upload fails

        # Make the actual post
        post_url = f"{self.facebook_base_url}/{page_id}/feed"

        try:
            response = self._make_api_request_with_retry(
                "POST",
                post_url,
                data=post_data
            )

            if response.get("success"):
                logger.info(f"Successfully posted to Facebook: {response['data']}")
                return response
            else:
                logger.error(f"Failed to post to Facebook: {response.get('error', 'Unknown error')}")
                return response
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}")
            return {"success": False, "error": str(e)}

    def post_to_instagram(self, caption: str, image_url: Optional[str] = None) -> Dict:
        """Post content to Instagram."""
        if not self.config["instagram"]["enabled"]:
            logger.warning("Instagram posting is disabled in config")
            return {"success": False, "error": "Instagram posting disabled"}

        access_token = self.config["instagram"]["access_token"]
        account_id = self.config["instagram"]["account_id"]

        # If image is provided, create an image container first
        if image_url:
            # Create the media object
            container_data = {
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token
            }

            container_url = f"{self.instagram_base_url}/{account_id}/media"

            try:
                container_response = self._make_api_request_with_retry(
                    "POST",
                    container_url,
                    data=container_data
                )

                if not container_response.get("success") or "id" not in container_response["data"]:
                    logger.error(f"Failed to create Instagram media container: {container_response}")
                    return container_response

                container_id = container_response["data"]["id"]

                # Publish the media
                publish_data = {
                    "creation_id": container_id,
                    "access_token": access_token
                }

                publish_url = f"{self.instagram_base_url}/{account_id}/media_publish"

                publish_response = self._make_api_request_with_retry(
                    "POST",
                    publish_url,
                    data=publish_data
                )

                if publish_response.get("success"):
                    logger.info(f"Successfully posted to Instagram: {publish_response['data']}")
                    return publish_response
                else:
                    logger.error(f"Failed to publish Instagram post: {publish_response}")
                    return publish_response

            except Exception as e:
                logger.error(f"Error posting to Instagram: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            # Text-only post (not supported by Instagram API, would need to add placeholder image)
            logger.warning("Instagram requires an image for posts. Only image posts are supported.")
            return {"success": False, "error": "Instagram requires an image for posts"}

    def _make_api_request_with_retry(self, method: str, url: str, data: Dict = None, max_retries: int = None) -> Dict:
        """Make an API request with retry logic."""
        if max_retries is None:
            max_retries = self.config["retry_settings"]["max_attempts"]

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, params=data)
                elif method.upper() == "POST":
                    response = requests.post(url, data=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()

                # Check if the response is in JSON format
                try:
                    result = response.json()
                except:
                    # If response isn't JSON, return as text but mark as error
                    # Facebook/Instagram APIs should return JSON
                    return {"success": True, "data": response.text}

                # Check for API-specific error responses
                if "error" in result:
                    raise Exception(f"API Error: {result['error']}")

                return {"success": True, "data": result}

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

    def fetch_engagement_metrics(self) -> Dict:
        """Fetch engagement metrics from Facebook and Instagram."""
        metrics = {"facebook": {}, "instagram": {}, "timestamp": datetime.now().isoformat()}

        # Fetch Facebook metrics if enabled
        if self.config["facebook"]["enabled"]:
            try:
                fb_metrics = self._fetch_facebook_metrics()
                metrics["facebook"] = fb_metrics
            except Exception as e:
                logger.error(f"Error fetching Facebook metrics: {str(e)}")
                metrics["facebook"] = {"error": str(e)}

        # Fetch Instagram metrics if enabled
        if self.config["instagram"]["enabled"]:
            try:
                ig_metrics = self._fetch_instagram_metrics()
                metrics["instagram"] = ig_metrics
            except Exception as e:
                logger.error(f"Error fetching Instagram metrics: {str(e)}")
                metrics["instagram"] = {"error": str(e)}

        # Store for reporting
        self.engagement_data[metrics["timestamp"]] = metrics

        return metrics

    def _fetch_facebook_metrics(self) -> Dict:
        """Fetch Facebook engagement metrics."""
        access_token = self.config["facebook"]["access_token"]
        page_id = self.config["facebook"]["page_id"]

        metrics_list = self.config["engagement_tracking"]["metrics"]

        # Only fetch insights if metrics are specified
        if not metrics_list:
            logger.info("No metrics specified, skipping Facebook insights fetch")
            return {"data": [], "message": "No metrics configured"}

        # Get page insights
        insights_url = f"{self.facebook_base_url}/{page_id}/insights"

        params = {
            "access_token": access_token,
            "metric": ",".join(metrics_list),
            "date_preset": "last_7d"  # Last 7 days
        }

        response = self._make_api_request_with_retry("GET", insights_url, data=params, max_retries=2)

        if response.get("success"):
            return response["data"]
        else:
            logger.error(f"Failed to fetch Facebook metrics: {response.get('error', 'Unknown error')}")
            return {"error": response.get("error", "Unknown error")}

    def _fetch_instagram_metrics(self) -> Dict:
        """Fetch Instagram engagement metrics."""
        access_token = self.config["instagram"]["access_token"]
        account_id = self.config["instagram"]["account_id"]

        # Get account media
        media_url = f"{self.instagram_base_url}/{account_id}/media"
        params = {
            "access_token": access_token,
            "fields": ",".join(["id", "caption", "like_count", "comments_count", "timestamp"])
        }

        response = self._make_api_request_with_retry("GET", media_url, data=params, max_retries=2)

        if response.get("success"):
            return response["data"]
        else:
            logger.error(f"Failed to fetch Instagram metrics: {response.get('error', 'Unknown error')}")
            return {"error": response.get("error", "Unknown error")}

    def generate_weekly_summary(self) -> Dict:
        """Generate a weekly engagement summary report."""
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
            "total_posts": 0,
            "facebook": {
                "total_engagement": 0,
                "average_engagement": 0,
                "top_performers": []
            },
            "instagram": {
                "total_engagement": 0,
                "average_engagement": 0,
                "top_performers": []
            }
        }

        # Process collected metrics
        if recent_metrics:
            fb_total_engagement = 0
            fb_engagement_count = 0
            ig_total_engagement = 0
            ig_engagement_count = 0

            for timestamp, metrics in recent_metrics.items():
                if "facebook" in metrics and "data" in metrics["facebook"]:
                    # Process Facebook metrics
                    fb_data = metrics["facebook"]["data"]
                    # Handle case where fb_data might be a direct list instead of dict with "data" key
                    if isinstance(fb_data, dict) and "data" in fb_data:
                        fb_entries = fb_data["data"]
                    elif isinstance(fb_data, list):
                        fb_entries = fb_data
                    else:
                        fb_entries = []

                    # Calculate engagement from insights
                    for entry in fb_entries:
                        if "values" in entry:
                            for value in entry["values"]:
                                if isinstance(value["value"], (int, float)):
                                    fb_total_engagement += value["value"]
                                    fb_engagement_count += 1

                if "instagram" in metrics and "data" in metrics["instagram"]:
                    # Process Instagram metrics
                    ig_data = metrics["instagram"]["data"]
                    # Handle case where ig_data might be a direct list instead of dict with "data" key
                    if isinstance(ig_data, dict) and "data" in ig_data:
                        ig_entries = ig_data["data"]
                    elif isinstance(ig_data, list):
                        ig_entries = ig_data
                    else:
                        ig_entries = []

                    for media in ig_entries:
                        likes = media.get("like_count", 0)
                        comments = media.get("comments_count", 0)
                        ig_total_engagement += likes + comments
                        ig_engagement_count += 1

            if fb_engagement_count > 0:
                summary["facebook"]["total_engagement"] = fb_total_engagement
                summary["facebook"]["average_engagement"] = fb_total_engagement / fb_engagement_count

            if ig_engagement_count > 0:
                summary["instagram"]["total_engagement"] = ig_total_engagement
                summary["instagram"]["average_engagement"] = ig_total_engagement / ig_engagement_count

            summary["total_posts"] = fb_engagement_count + ig_engagement_count

        return summary

    def queue_content(self, content: Dict) -> str:
        """Queue content for scheduled posting."""
        content_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.content_queue)}"
        content["id"] = content_id
        content["scheduled_at"] = datetime.now().isoformat()

        self.content_queue.append(content)
        logger.info(f"Queued content with ID: {content_id}")

        return content_id

    def process_content_queue(self):
        """Process the content queue according to schedule."""
        if not self.config["posting_schedule"]["enabled"]:
            logger.info("Content queue processing is disabled")
            return

        # Check if current time matches schedule
        current_time = datetime.now()
        current_day = current_time.strftime("%a").lower()[:3]  # mon, tue, etc.
        current_hour_min = current_time.strftime("%H:%M")

        schedule_day = self.config["posting_schedule"]["days"]
        schedule_time = self.config["posting_schedule"]["time"]

        if current_day in schedule_day and current_hour_min == schedule_time:
            logger.info(f"Processing queue for scheduled time: {current_day} {current_hour_min}")

            # Process queue (in real implementation, you'd have more sophisticated scheduling)
            processed = 0
            for content in self.content_queue[:]:  # Copy to avoid modification during iteration
                # Post to both platforms if enabled
                success = True

                if content.get("platforms", {}).get("facebook", True) and self.config["facebook"]["enabled"]:
                    result = self.post_to_facebook(
                        content.get("message", ""),
                        content.get("image_url"),
                        content.get("link")
                    )
                    if not result.get("success"):
                        success = False

                if content.get("platforms", {}).get("instagram", True) and self.config["instagram"]["enabled"]:
                    result = self.post_to_instagram(
                        content.get("message", ""),
                        content.get("image_url")
                    )
                    if not result.get("success"):
                        success = False

                if success:
                    logger.info(f"Successfully processed queued content: {content['id']}")
                    self.content_queue.remove(content)
                    processed += 1
                else:
                    logger.warning(f"Failed to process queued content: {content['id']}")

        else:
            logger.debug(f"Not scheduled time. Current: {current_day} {current_hour_min}, Scheduled: {schedule_day} {schedule_time}")

    def save_report(self, report_data: Dict, filename: str = None):
        """Save the engagement report to a file."""
        if not filename:
            filename = f"weekly_summary_{datetime.now().strftime('%Y%m%d')}.json"

        reports_dir = Path("Reports")
        reports_dir.mkdir(exist_ok=True)

        filepath = reports_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Saved report to {filepath}")
        return str(filepath)

# Example usage
if __name__ == "__main__":
    # Initialize the Social Poster
    poster = SocialPosterFBI()

    # Example: Queue content for posting
    content = {
        "message": "Check out our latest product update! 🚀",
        "image_url": "https://example.com/image.jpg",
        "link": "https://example.com/product",
        "platforms": {"facebook": True, "instagram": True}
    }

    content_id = poster.queue_content(content)
    print(f"Queued content with ID: {content_id}")

    # Example: Post content now (not using queue)
    print("\nPosting to Facebook...")
    fb_result = poster.post_to_facebook(
        "This is a REAL test post from my automation system 🚀🔥",
        None,
        None
    )
    print(f"Facebook post result: {fb_result}")

    print("\nPosting to Instagram...")
    ig_result = poster.post_to_instagram(
        "This is a REAL test post from my automation system 🚀🔥",
        None
    )
    print(f"Instagram post result: {ig_result}")

    # Example: Fetch and display engagement metrics
    print("\nFetching engagement metrics...")
    metrics = poster.fetch_engagement_metrics()
    print(f"Engagement metrics: {json.dumps(metrics, indent=2)}")

    # Example: Generate and save weekly summary
    print("\nGenerating weekly summary...")
    summary = poster.generate_weekly_summary()
    print(f"Weekly summary: {json.dumps(summary, indent=2)}")

    report_path = poster.save_report(summary)
    print(f"Report saved to: {report_path}")