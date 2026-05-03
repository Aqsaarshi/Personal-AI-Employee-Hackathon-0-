# CEO Briefing Generator Skill

## Overview
The CEO Briefing Generator skill creates comprehensive weekly reports including revenue, expenses, profit/loss, social media performance, leads, opportunities, risks, and recommendations. It aggregates data from all relevant skills and outputs reports in Markdown format.

## Features
- **Comprehensive Data Aggregation**: Gathers data from Ledger Manager, Social Posters, Cross-Domain Manager, and Audit Logger
- **Financial Summary**: Revenue, expenses, profit/loss with category breakdowns
- **Social Media Performance**: Engagement metrics from Facebook/Instagram and Twitter/X
- **Leads & Opportunities**: Task pipeline and domain-specific summaries
- **Risk Analysis**: Identification of operational and financial risks
- **Recommendations**: Actionable insights based on data analysis
- **Performance Metrics**: System performance tracking from audit logs
- **Professional Reporting**: Well-formatted Markdown reports

## Configuration
The skill uses `config.json` for report settings:

```json
{
  "reporting": {
    "output_format": ["markdown", "pdf"],
    "default_format": "markdown",
    "output_path": "Reports/CEO_Reports",
    "include": {
      "financial_summary": true,
      "social_media_performance": true,
      "leads_and_opportunities": true,
      "risks_and_recommendations": true,
      "performance_metrics": true
    }
  },
  "data_sources": {
    "ledger_manager": {
      "enabled": true,
      "path": "Skills/Ledger_Manager/ledger_manager.py"
    },
    "social_poster_fbi": {
      "enabled": true,
      "path": "Skills/SocialPoster_FBI/social_poster_fbi.py"
    },
    "social_poster_twitter": {
      "enabled": true,
      "path": "Skills/SocialPoster_Twitter/social_poster_twitter.py"
    },
    "cross_domain_manager": {
      "enabled": true,
      "path": "Skills/CrossDomain_Manager/crossdomain_manager.py"
    }
  },
  "report_schedule": {
    "enabled": true,
    "day": "fri",
    "time": "17:00"
  }
}
```

## Report Sections

### Executive Summary
- High-level overview of the week's performance
- Key metrics and highlights

### Financial Summary
- Total income and expenses
- Category breakdown of income and expenses
- Net profit/loss for the period

### Social Media Performance
- Engagement metrics from Facebook/Instagram
- Engagement metrics from Twitter/X
- Performance trends and insights

### Leads and Opportunities
- Total tasks in pipeline
- Breakdown by domain (Personal/Business)
- Status distribution of tasks

### Risks and Recommendations
- Identified operational and financial risks
- Priority-based recommendations
- Action items for management

### System Performance Metrics
- Total actions executed
- Success/failure rates
- Performance bottlenecks
- Slowest executing operations

## Usage Examples

### Generate Weekly Report
```python
from ceo_briefing_generator import CEOBriefingGenerator

generator = CEOBriefingGenerator()

# Generate report for current week
saved_files = generator.generate_weekly_report()
print(f"Report saved to: {saved_files}")

# Generate report for specific week
saved_files = generator.generate_weekly_report("2026-02-15")
print(f"Report saved to: {saved_files}")
```

### Get Raw Data Without Generating Report
```python
# Get the raw data that would go into the report
report_data = generator.get_weekly_summary()

# Access specific sections
financial_data = report_data["financial_summary"]
social_data = report_data["social_media_performance"]
```

## Data Aggregation Logic

### Financial Data
- Integrates with Ledger Manager to get income, expenses, and profit/loss
- Calculates category breakdowns
- Provides trend analysis with previous periods

### Social Media Data
- Fetches engagement metrics from SocialPoster_FBI and SocialPoster_Twitter
- Aggregates likes, comments, shares, retweets across platforms
- Calculates engagement rates and trends

### Task Data
- Retrieves task summaries from CrossDomain Manager
- Categorizes tasks by domain (Personal/Business)
- Provides status breakdowns and priorities

### Risk Analysis
- Analyzes audit logs for failed operations
- Reviews financial trends for potential issues
- Evaluates social media performance for engagement problems

## Output Format
The generated report follows a structured Markdown format with:
- Clear section headers
- Bullet points for key metrics
- Tables for detailed breakdowns where appropriate
- Professional formatting suitable for executive consumption

The CEO Briefing Generator provides a comprehensive view of company performance across all operational areas in a format designed for executive decision-making.