"""
Unified Social Media Manager
Manages both Facebook/Instagram and Twitter/X posting in a unified interface
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI
from Skills.SocialPoster_Twitter.social_poster_twitter import SocialPosterTwitter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedSocialManager:
    def __init__(self):
        """Initialize both social media posters."""
        self.facebook_instagram_poster = SocialPosterFBI()
        self.twitter_poster = SocialPosterTwitter()

    def post_unified(self, content: str, platforms: List[str] = None, image_url: str = None) -> Dict:
        """Post content to multiple platforms in a unified way."""
        if platforms is None:
            platforms = ["facebook", "instagram", "twitter"]

        results = {}

        # Post to Facebook if enabled and requested
        if "facebook" in platforms and self.facebook_instagram_poster.config["facebook"]["enabled"]:
            try:
                results["facebook"] = self.facebook_instagram_poster.post_to_facebook(
                    content, image_url
                )
            except Exception as e:
                logger.error(f"Error posting to Facebook: {str(e)}")
                results["facebook"] = {"success": False, "error": str(e)}

        # Post to Instagram if enabled and requested
        if "instagram" in platforms and self.facebook_instagram_poster.config["instagram"]["enabled"]:
            try:
                results["instagram"] = self.facebook_instagram_poster.post_to_instagram(
                    content, image_url
                )
            except Exception as e:
                logger.error(f"Error posting to Instagram: {str(e)}")
                results["instagram"] = {"success": False, "error": str(e)}

        # Post to Twitter if enabled and requested
        if "twitter" in platforms and self.twitter_poster.config["twitter"]["enabled"]:
            try:
                results["twitter"] = self.twitter_poster.post_tweet(content)
            except Exception as e:
                logger.error(f"Error posting to Twitter: {str(e)}")
                results["twitter"] = {"success": False, "error": str(e)}

        return results

    def queue_unified_content(self, content: str, platforms: List[str] = None, image_url: str = None) -> Dict:
        """Queue content for all requested platforms."""
        if platforms is None:
            platforms = ["facebook", "instagram", "twitter"]

        results = {}

        # Queue for Facebook/Instagram if requested
        if "facebook" in platforms or "instagram" in platforms:
            content_data = {
                "message": content,
                "image_url": image_url,
                "platforms": {"facebook": "facebook" in platforms, "instagram": "instagram" in platforms}
            }
            results["facebook_instagram"] = self.facebook_instagram_poster.queue_content(content_data)

        # Queue for Twitter if requested
        if "twitter" in platforms:
            results["twitter"] = self.twitter_poster.queue_tweet(content, image_url)

        return results

    def fetch_all_engagement_metrics(self) -> Dict:
        """Fetch engagement metrics from all platforms."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "facebook_instagram": {},
            "twitter": {}
        }

        try:
            # Fetch Facebook/Instagram metrics
            metrics["facebook_instagram"] = self.facebook_instagram_poster.fetch_engagement_metrics()
        except Exception as e:
            logger.error(f"Error fetching Facebook/Instagram metrics: {str(e)}")
            metrics["facebook_instagram"] = {"error": str(e)}

        try:
            # Fetch Twitter metrics
            metrics["twitter"] = self.twitter_poster.fetch_engagement_metrics()
        except Exception as e:
            logger.error(f"Error fetching Twitter metrics: {str(e)}")
            metrics["twitter"] = {"error": str(e)}

        return metrics

    def generate_unified_weekly_summary(self) -> Dict:
        """Generate a unified weekly summary across all platforms."""
        summary = {
            "period_start": (datetime.now() - timedelta(days=7)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "total_posts": 0,
            "all_platforms": {
                "facebook": {},
                "instagram": {},
                "twitter": {}
            },
            "unified_metrics": {
                "total_engagement": 0,
                "average_engagement": 0,
                "top_performers": {}
            }
        }

        # Get individual platform summaries
        try:
            fb_ig_summary = self.facebook_instagram_poster.generate_weekly_summary()
            summary["all_platforms"]["facebook"] = fb_ig_summary.get("facebook", {})
            summary["all_platforms"]["instagram"] = fb_ig_summary.get("instagram", {})
            summary["total_posts"] += fb_ig_summary.get("total_posts", 0)
        except Exception as e:
            logger.error(f"Error generating Facebook/Instagram summary: {str(e)}")

        try:
            twitter_summary = self.twitter_poster.generate_weekly_summary()
            summary["all_platforms"]["twitter"] = twitter_summary.get("twitter", {})
            summary["total_posts"] += twitter_summary.get("total_tweets", 0)
        except Exception as e:
            logger.error(f"Error generating Twitter summary: {str(e)}")

        return summary

    def save_unified_report(self, report_data: Dict, filename: str = None) -> str:
        """Save the unified engagement report to a file."""
        if not filename:
            filename = f"unified_social_summary_{datetime.now().strftime('%Y%m%d')}.json"

        reports_dir = Path("Reports")
        reports_dir.mkdir(exist_ok=True)

        filepath = reports_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Saved unified report to {filepath}")
        return str(filepath)

# Example usage
if __name__ == "__main__":
    # Initialize the unified manager
    manager = UnifiedSocialManager()

    print("Unified Social Media Manager initialized successfully!")
    print("Features:")
    print("- Unified posting across Facebook, Instagram, and Twitter")
    print("- Centralized engagement metrics fetching")
    print("- Cross-platform reporting")
    print("- Content queue management")