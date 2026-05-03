# CEO Briefing Generator Skill

## Purpose
The CEO Briefing Generator skill creates comprehensive weekly reports including revenue, expenses, profit/loss, social media performance, leads, opportunities, risks, and recommendations. It aggregates data from all relevant skills and outputs reports in Markdown or PDF format.

## Configuration
The skill requires a configuration file with report settings and output options:

```json
{
  "reporting": {
    "output_format": ["markdown", "pdf"], // Can specify both
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
    }
  },
  "report_schedule": {
    "enabled": true,
    "day": "fri", // day of week to generate
    "time": "17:00" // time to generate
  }
}
```

## Core Functions

### 1. Report Template
- Professional template for CEO reports
- Modular sections that can be enabled/disabled
- Branding and formatting options
- Consistent structure across reports

### 2. Data Aggregation Logic
- Extract data from all relevant skills
- Financial data from Ledger Manager
- Social media metrics from Social Posters
- Performance data from Audit Logger
- Risk and opportunity data from all sources

### 3. Sample Generated Report
- Complete example of the output format
- Sample data demonstrating all report sections
- Professional presentation of metrics
- Actionable insights and recommendations