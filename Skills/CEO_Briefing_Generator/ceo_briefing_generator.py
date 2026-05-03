"""
CEO Briefing Generator Skill
Generates comprehensive weekly reports for CEO
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.SocialPoster_FBI.social_poster_fbi import SocialPosterFBI
from Skills.SocialPoster_Twitter.social_poster_twitter import SocialPosterTwitter
from Skills.Audit_Logger.audit_logger import get_audit_logger
from Skills.CrossDomain_Manager.crossdomain_manager import CrossDomainManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CEOBriefingGenerator:
    def __init__(self, config_path: str = "Skills/CEO_Briefing_Generator/config.json"):
        """Initialize the CEO Briefing Generator with configuration."""
        self.config_path = config_path
        self.config = self.load_config()

        # Create reports directory if it doesn't exist
        reports_dir = self.config["reporting"]["output_path"]
        os.makedirs(reports_dir, exist_ok=True)

        # Initialize data sources
        self.ledger_manager = None
        self.social_poster_fbi = None
        self.social_poster_twitter = None
        self.audit_logger = None
        self.cross_domain_manager = None

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "reporting": {
                "output_format": ["markdown", "pdf"],
                "default_format": "markdown",
                "output_path": "Reports/CEO_Reports",
                "include": {
                    "financial_summary": True,
                    "social_media_performance": True,
                    "leads_and_opportunities": True,
                    "risks_and_recommendations": True,
                    "performance_metrics": True
                }
            },
            "data_sources": {
                "ledger_manager": {
                    "enabled": True,
                    "path": "Skills/Ledger_Manager/ledger_manager.py"
                },
                "social_poster_fbi": {
                    "enabled": True,
                    "path": "Skills/SocialPoster_FBI/social_poster_fbi.py"
                },
                "social_poster_twitter": {
                    "enabled": True,
                    "path": "Skills/SocialPoster_Twitter/social_poster_twitter.py"
                },
                "cross_domain_manager": {
                    "enabled": True,
                    "path": "Skills/CrossDomain_Manager/crossdomain_manager.py"
                }
            },
            "report_schedule": {
                "enabled": True,
                "day": "fri",
                "time": "17:00"
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

    def _init_data_sources(self):
        """Initialize all data sources."""
        try:
            if self.config["data_sources"]["ledger_manager"]["enabled"]:
                self.ledger_manager = LedgerManager()
        except Exception as e:
            logger.warning(f"Could not initialize Ledger Manager: {e}")

        try:
            if self.config["data_sources"]["social_poster_fbi"]["enabled"]:
                self.social_poster_fbi = SocialPosterFBI()
        except Exception as e:
            logger.warning(f"Could not initialize SocialPoster_FBI: {e}")

        try:
            if self.config["data_sources"]["social_poster_twitter"]["enabled"]:
                self.social_poster_twitter = SocialPosterTwitter()
        except Exception as e:
            logger.warning(f"Could not initialize SocialPoster_Twitter: {e}")

        try:
            self.audit_logger = get_audit_logger()
        except Exception as e:
            logger.warning(f"Could not initialize Audit Logger: {e}")

        try:
            if self.config["data_sources"]["cross_domain_manager"]["enabled"]:
                self.cross_domain_manager = CrossDomainManager()
        except Exception as e:
            logger.warning(f"Could not initialize CrossDomainManager: {e}")

    def generate_weekly_data(self, week_start: str = None) -> Dict:
        """Aggregate data for the weekly report."""
        if not week_start:
            # Calculate the start of the current week (Monday)
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start_dt = today - timedelta(days=days_since_monday)
            week_start = week_start_dt.strftime("%Y-%m-%d")
        else:
            week_start_dt = datetime.strptime(week_start, "%Y-%m-%d")

        # Calculate the end of the week (Sunday)
        week_end_dt = week_start_dt + timedelta(days=6)
        week_end = week_end_dt.strftime("%Y-%m-%d")

        # Initialize the data dictionary
        report_data = {
            "report_date": datetime.now().isoformat(),
            "reporting_period": {
                "start": week_start,
                "end": week_end,
                "formatted_start": week_start_dt.strftime("%B %d, %Y"),
                "formatted_end": week_end_dt.strftime("%B %d, %Y")
            },
            "financial_summary": {},
            "social_media_performance": {},
            "leads_and_opportunities": {},
            "risks_and_recommendations": {},
            "performance_metrics": {}
        }

        # Get financial data
        if self.config["reporting"]["include"]["financial_summary"] and self.ledger_manager:
            try:
                financial_summary = self.ledger_manager.generate_weekly_summary(week_start)
                report_data["financial_summary"] = financial_summary
            except Exception as e:
                logger.error(f"Error getting financial data: {e}")
                report_data["financial_summary"] = {"error": str(e)}

        # Get social media data
        if self.config["reporting"]["include"]["social_media_performance"]:
            social_data = {}

            if self.social_poster_fbi:
                try:
                    fb_ig_metrics = self.social_poster_fbi.fetch_engagement_metrics()
                    social_data["facebook_instagram"] = fb_ig_metrics
                except Exception as e:
                    logger.error(f"Error getting Facebook/Instagram data: {e}")
                    social_data["facebook_instagram"] = {"error": str(e)}

            if self.social_poster_twitter:
                try:
                    twitter_metrics = self.social_poster_twitter.fetch_engagement_metrics()
                    social_data["twitter"] = twitter_metrics
                except Exception as e:
                    logger.error(f"Error getting Twitter data: {e}")
                    social_data["twitter"] = {"error": str(e)}

            report_data["social_media_performance"] = social_data

        # Get leads and opportunities (from CrossDomain Manager tasks)
        if self.config["reporting"]["include"]["leads_and_opportunities"] and self.cross_domain_manager:
            try:
                domain_summary = self.cross_domain_manager.get_unified_summary()
                report_data["leads_and_opportunities"] = {
                    "domain_summary": domain_summary,
                    "total_tasks": sum(
                        domain_info["total_tasks"]
                        for domain_info in domain_summary.get("domains", {}).values()
                    )
                }
            except Exception as e:
                logger.error(f"Error getting leads/opportunities data: {e}")
                report_data["leads_and_opportunities"] = {"error": str(e)}

        # Get risks and recommendations (from audit logs and financial trends)
        if self.config["reporting"]["include"]["risks_and_recommendations"]:
            risks_recommendations = self._analyze_risks_and_recommendations(week_start, week_end)
            report_data["risks_and_recommendations"] = risks_recommendations

        # Get performance metrics
        if self.config["reporting"]["include"]["performance_metrics"] and self.audit_logger:
            try:
                performance_data = self.audit_logger.get_performance_summary(week_start, week_end)
                report_data["performance_metrics"] = performance_data
            except Exception as e:
                logger.error(f"Error getting performance metrics: {e}")
                report_data["performance_metrics"] = {"error": str(e)}

        return report_data

    def _analyze_risks_and_recommendations(self, start_date: str, end_date: str) -> Dict:
        """Analyze risks and generate recommendations."""
        risks = []
        recommendations = []

        # Check for failed actions from audit logs
        if self.audit_logger:
            try:
                failed_actions = self.audit_logger.get_failed_actions(start_date, end_date)
                if len(failed_actions) > 5:  # More than 5 failures is concerning
                    risks.append({
                        "type": "operational",
                        "severity": "high",
                        "description": f"High number of failed operations ({len(failed_actions)}) during the week",
                        "suggestion": "Review and address system reliability issues"
                    })
            except Exception:
                pass  # Continue even if audit logs are unavailable

        # Financial risks (if available)
        if self.ledger_manager:
            try:
                weekly_summary = self.ledger_manager.generate_weekly_summary(start_date)
                if weekly_summary.get("profit_loss", 0) < 0:
                    risks.append({
                        "type": "financial",
                        "severity": "high",
                        "description": "Company reported a net loss this week",
                        "suggestion": "Review expenses and identify cost reduction opportunities"
                    })

                # Check if marketing spend is too high relative to income
                expenses = weekly_summary.get("expenses_by_category", {})
                income = weekly_summary.get("total_income", 0)
                marketing_expense = expenses.get("marketing", 0)

                if income > 0 and (marketing_expense / income) > 0.15:
                    recommendations.append({
                        "type": "marketing",
                        "priority": "medium",
                        "description": "Marketing expenses exceed 15% of income",
                        "suggestion": "Optimize marketing spend efficiency"
                    })
            except Exception:
                pass  # Continue even if financial data is unavailable

        # Social media performance
        social_issues = []
        if self.social_poster_fbi:
            try:
                fb_summary = self.social_poster_fbi.generate_weekly_summary()
                # If engagement is low, flag as recommendation
                avg_engagement = fb_summary.get("facebook", {}).get("average_engagement", 0)
                if avg_engagement < 10:  # Assuming low engagement threshold
                    recommendations.append({
                        "type": "social_media",
                        "priority": "medium",
                        "description": "Low Facebook engagement",
                        "suggestion": "Review content strategy and posting times"
                    })
            except Exception:
                pass

        if self.social_poster_twitter:
            try:
                tw_summary = self.social_poster_twitter.generate_weekly_summary()
                avg_engagement = tw_summary.get("twitter", {}).get("average_engagement", 0)
                if avg_engagement < 5:  # Assuming low engagement threshold
                    recommendations.append({
                        "type": "social_media",
                        "priority": "medium",
                        "description": "Low Twitter engagement",
                        "suggestion": "Review tweet strategy and timing"
                    })
            except Exception:
                pass

        return {
            "risks": risks,
            "recommendations": recommendations,
            "summary": {
                "total_risks": len(risks),
                "total_recommendations": len(recommendations)
            }
        }

    def generate_markdown_report(self, report_data: Dict) -> str:
        """Generate a Markdown formatted report."""
        report_date = datetime.now().strftime("%B %d, %Y")
        period = f"{report_data['reporting_period']['formatted_start']} - {report_data['reporting_period']['formatted_end']}"

        markdown = f"""# CEO Weekly Briefing Report
**Report Date:** {report_date}
**Reporting Period:** {period}

---

## Executive Summary
This report provides a comprehensive overview of company performance for the week, including financial metrics, social media engagement, operational activities, and recommendations for improvement.

---

"""

        # Financial Summary
        if report_data["financial_summary"] and self.config["reporting"]["include"]["financial_summary"]:
            summary = report_data["financial_summary"]
            markdown += f"""## Financial Summary
- **Total Income:** ${summary.get('total_income', 0):,.2f}
- **Total Expenses:** ${summary.get('total_expenses', 0):,.2f}
- **Net Profit/Loss:** ${summary.get('profit_loss', 0):,.2f}
- **Currency:** {summary.get('currency', 'USD')}

"""
            if summary.get('income_by_category'):
                markdown += "**Income Breakdown by Category:**\n"
                for category, amount in sorted(summary['income_by_category'].items(), key=lambda x: x[1], reverse=True):
                    markdown += f"  - {category.title()}: ${amount:,.2f}\n"
                markdown += "\n"

            if summary.get('expenses_by_category'):
                markdown += "**Expense Breakdown by Category:**\n"
                for category, amount in sorted(summary['expenses_by_category'].items(), key=lambda x: x[1], reverse=True):
                    markdown += f"  - {category.title()}: ${amount:,.2f}\n"
                markdown += "\n"

        # Social Media Performance
        if report_data["social_media_performance"] and self.config["reporting"]["include"]["social_media_performance"]:
            social_data = report_data["social_media_performance"]
            markdown += "## Social Media Performance\n"

            if "facebook_instagram" in social_data:
                markdown += "**Facebook/Instagram:**\n"
                if social_data["facebook_instagram"].get("error"):
                    markdown += f"  - *Error retrieving data: {social_data['facebook_instagram']['error']}*\n"
                else:
                    # Simplified display of social metrics
                    markdown += "  - Data collected successfully\n"
                markdown += "\n"

            if "twitter" in social_data:
                markdown += "**Twitter/X:**\n"
                if social_data["twitter"].get("error"):
                    markdown += f"  - *Error retrieving data: {social_data['twitter']['error']}*\n"
                else:
                    # Simplified display of twitter metrics
                    markdown += "  - Data collected successfully\n"
                markdown += "\n"

        # Leads and Opportunities
        if report_data["leads_and_opportunities"] and self.config["reporting"]["include"]["leads_and_opportunities"]:
            leads_data = report_data["leads_and_opportunities"]
            markdown += "## Leads and Opportunities\n"
            if "total_tasks" in leads_data:
                markdown += f"- **Total Tasks in Pipeline:** {leads_data['total_tasks']}\n"

            if "domain_summary" in leads_data:
                domains = leads_data["domain_summary"].get("domains", {})
                for domain, domain_info in domains.items():
                    total_tasks = domain_info.get("total_tasks", 0)
                    markdown += f"- **{domain.title()} Domain:** {total_tasks} tasks\n"
                    by_status = domain_info.get("by_status", {})
                    if by_status:
                        markdown += f"  - Status breakdown: {', '.join([f'{k}: {v}' for k, v in by_status.items()])}\n"
            markdown += "\n"

        # Risks and Recommendations
        if report_data["risks_and_recommendations"] and self.config["reporting"]["include"]["risks_and_recommendations"]:
            risk_data = report_data["risks_and_recommendations"]
            markdown += "## Risks and Recommendations\n"

            if risk_data.get("summary", {}).get("total_risks", 0) > 0:
                markdown += f"**Identified Risks ({risk_data['summary']['total_risks']}):**\n"
                for risk in risk_data.get("risks", []):
                    markdown += f"- **{risk['severity'].title()} Risk:** {risk['description']}\n"
                    markdown += f"  - *Suggestion:* {risk['suggestion']}\n"
                markdown += "\n"

            if risk_data.get("summary", {}).get("total_recommendations", 0) > 0:
                markdown += f"**Recommendations ({risk_data['summary']['total_recommendations']}):**\n"
                for rec in risk_data.get("recommendations", []):
                    priority = rec.get('priority', 'medium').title()
                    markdown += f"- **{priority} Priority:** {rec['description']}\n"
                    markdown += f"  - *Suggestion:* {rec['suggestion']}\n"
                markdown += "\n"

        # Performance Metrics
        if report_data["performance_metrics"] and self.config["reporting"]["include"]["performance_metrics"]:
            perf_data = report_data["performance_metrics"]
            markdown += "## System Performance Metrics\n"
            markdown += f"- **Total Actions:** {perf_data.get('total_actions', 0)}\n"
            markdown += f"- **Successful Actions:** {perf_data.get('successful_actions', 0)}\n"
            markdown += f"- **Failed Actions:** {perf_data.get('failed_actions', 0)}\n"
            markdown += f"- **Average Duration:** {perf_data.get('avg_duration', 0):.2f}s\n"

            if perf_data.get('slowest_action'):
                slow_action = perf_data['slowest_action']
                markdown += f"- **Slowest Action:** {slow_action.get('skill_name', 'N/A')}.{slow_action.get('action_type', 'N/A')} ({slow_action.get('performance_metrics', {}).get('duration_seconds', 0):.2f}s)\n"
            markdown += "\n"

        # Close the report
        markdown += "---\n"
        markdown += f"*Report generated by AI Executive Assistant on {report_date}*\n"

        return markdown

    def save_report(self, report_data: Dict, output_formats: List[str] = None) -> List[str]:
        """Save the report in specified formats."""
        if output_formats is None:
            output_formats = self.config["reporting"]["output_format"]

        saved_files = []
        report_date = datetime.now().strftime("%Y%m%d")
        report_filename_base = f"CEO_Weekly_Briefing_{report_date}"

        # Generate Markdown report
        if "markdown" in output_formats:
            markdown_content = self.generate_markdown_report(report_data)

            # Create the markdown file
            markdown_path = os.path.join(
                self.config["reporting"]["output_path"],
                f"{report_filename_base}.md"
            )

            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            saved_files.append(markdown_path)
            logger.info(f"Markdown report saved to {markdown_path}")

        # Generate PDF report (as a simple text file since we don't have a PDF library)
        if "pdf" in output_formats:
            # For now, we'll create a simple text version, but in a real implementation
            # we would use a PDF generation library like ReportLab or WeasyPrint
            markdown_content = self.generate_markdown_report(report_data)

            pdf_path = os.path.join(
                self.config["reporting"]["output_path"],
                f"{report_filename_base}.txt"  # Using .txt as placeholder for PDF
            )

            with open(pdf_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            saved_files.append(pdf_path)
            logger.info(f"PDF-style report saved to {pdf_path}")

        return saved_files

    def generate_weekly_report(self, week_start: str = None) -> List[str]:
        """Generate the complete weekly CEO report."""
        # Initialize data sources
        self._init_data_sources()

        # Generate the data
        report_data = self.generate_weekly_data(week_start)

        # Save the report
        saved_files = self.save_report(report_data)

        logger.info(f"Weekly CEO report generated successfully: {saved_files}")
        return saved_files

    def get_weekly_summary(self, week_start: str = None) -> Dict:
        """Get the weekly summary data without generating a report."""
        # Initialize data sources
        self._init_data_sources()

        # Generate the data
        report_data = self.generate_weekly_data(week_start)

        return report_data

# Example usage
if __name__ == "__main__":
    generator = CEOBriefingGenerator()

    print("CEO Briefing Generator initialized successfully!")
    print("Features:")
    print("- Comprehensive data aggregation from all skills")
    print("- Financial summary with income, expenses, profit/loss")
    print("- Social media performance metrics")
    print("- Leads and opportunities tracking")
    print("- Risk analysis and recommendations")
    print("- Performance metrics from audit logs")
    print("- Markdown report generation")
    print("- Scheduled report generation capability")