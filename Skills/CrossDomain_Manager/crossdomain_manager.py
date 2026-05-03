"""
Cross-Domain Manager Skill
Manages both Personal and Business tasks in a unified system
Integrates data from all watcher scripts and social media sources
"""
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the project root to the path so we can import other modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossDomainManager:
    def __init__(self, config_path: str = "Skills/CrossDomain_Manager/config.json"):
        """Initialize the Cross-Domain Manager with configuration."""
        self.config_path = config_path
        self.config = self.load_config()
        self.domains = self.config.get("domains", {})
        self.integration_sources = self.config.get("integration_sources", [])

        # Create domain folders if they don't exist
        for domain, settings in self.domains.items():
            folder = settings.get("folder", f"{domain.capitalize()}_Tasks")
            if not os.path.exists(folder):
                os.makedirs(folder)
                logger.info(f"Created {domain} domain folder: {folder}")

    def load_config(self) -> Dict:
        """Load configuration from file, create default if doesn't exist."""
        default_config = {
            "domains": {
                "personal": {
                    "folder": "Personal_Tasks",
                    "priorities": ["low", "medium", "high"],
                    "default_deadline": "7d"
                },
                "business": {
                    "folder": "Business_Tasks",
                    "priorities": ["low", "medium", "high", "critical"],
                    "default_deadline": "3d"
                }
            },
            "integration_sources": [
                "gmail",
                "linkedin",
                "whatsapp",
                "vault",
                "social_media"
            ]
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_path}")
            return default_config

    def classify_task(self, raw_data: Dict) -> str:
        """Classify a task as personal or business based on content analysis."""
        content = raw_data.get("content", "").lower()

        # Keywords for business tasks
        business_keywords = [
            "client", "meeting", "project", "revenue", "sales",
            "business", "contract", "proposal", "invoice", "quote",
            "corporate", "team", "strategy", "finance", "budget"
        ]

        # Keywords for personal tasks
        personal_keywords = [
            "personal", "family", "health", "appointment", "doctor",
            "shopping", "personal", "private", "home", "vacation",
            "friend", "hobby", "exercise", "personal care"
        ]

        business_score = sum(1 for keyword in business_keywords if keyword in content)
        personal_score = sum(1 for keyword in personal_keywords if keyword in content)

        if business_score > personal_score:
            return "business"
        elif personal_score > business_score:
            return "personal"
        else:
            # Default to business if no clear classification
            return "business"

    def create_task(self, raw_data: Dict) -> str:
        """Create a structured task file based on raw data from watchers."""
        # Classify the task
        domain = self.classify_task(raw_data)
        domain_config = self.domains[domain]

        # Create task metadata
        task_id = f"{domain}_{raw_data.get('source', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task_title = raw_data.get("title", "Untitled Task")
        task_content = raw_data.get("content", "")
        source = raw_data.get("source", "unknown")
        source_id = raw_data.get("source_id", "")

        # Determine priority
        priority = self.determine_priority(raw_data, domain)

        # Set deadline
        deadline = self.calculate_deadline(raw_data, domain_config)

        # Create task structure
        task_data = {
            "id": task_id,
            "title": task_title,
            "content": task_content,
            "domain": domain,
            "source": source,
            "source_id": source_id,
            "priority": priority,
            "status": "created",
            "deadline": deadline,
            "created_at": datetime.now().isoformat(),
            "assigned_to": raw_data.get("assigned_to", "unassigned"),
            "tags": raw_data.get("tags", []),
            "dependencies": raw_data.get("dependencies", [])
        }

        # Save task file
        folder = domain_config["folder"]
        task_file = os.path.join(folder, f"{task_id}.md")

        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(f"# {task_title}\n\n")
            f.write(f"**ID:** {task_id}\n")
            f.write(f"**Domain:** {domain}\n")
            f.write(f"**Source:** {source}\n")
            f.write(f"**Priority:** {priority}\n")
            f.write(f"**Status:** created\n")
            f.write(f"**Deadline:** {deadline}\n")
            f.write(f"**Created:** {task_data['created_at']}\n")
            f.write(f"**Assigned to:** {task_data['assigned_to']}\n")
            f.write(f"**Tags:** {', '.join(task_data['tags'])}\n")
            f.write(f"**Dependencies:** {', '.join(task_data['dependencies'])}\n\n")
            f.write("---\n\n")
            f.write("## Description\n")
            f.write(task_content + "\n\n")
            f.write("---\n\n")
            f.write("## Task Progress\n")
            f.write("- [ ] Initial assessment\n")
            f.write("- [ ] Planning phase\n")
            f.write("- [ ] Execution phase\n")
            f.write("- [ ] Completion review\n\n")
            f.write("---\n\n")
            f.write("## Notes\n")
            f.write("_Add notes here as the task progresses_\n")

        logger.info(f"Created {domain} task: {task_id}")
        return task_file

    def determine_priority(self, raw_data: Dict, domain: str) -> str:
        """Determine task priority based on various factors."""
        domain_config = self.domains[domain]
        priorities = domain_config["priorities"]

        # Extract factors that influence priority
        content = raw_data.get("content", "").lower()
        urgency_keywords = [
            "urgent", "asap", "immediately", "today", "now",
            "critical", "emergency", "important"
        ]

        # Count urgency indicators
        urgency_score = sum(1 for keyword in urgency_keywords if keyword in content)

        # Default to medium priority if no specific indicators
        if urgency_score == 0:
            return "medium" if "medium" in priorities else priorities[0]

        # Use higher priority for more urgent indicators
        if urgency_score >= 2:
            return "critical" if "critical" in priorities else "high"
        else:
            return "high" if "high" in priorities else "medium"

    def calculate_deadline(self, raw_data: Dict, domain_config: Dict) -> str:
        """Calculate deadline based on raw data and domain defaults."""
        # Check if deadline is specified in raw data
        if "deadline" in raw_data:
            return raw_data["deadline"]

        # Use domain default
        default_deadline = domain_config.get("default_deadline", "3d")

        # Parse the deadline format (e.g., "3d", "1w", "7d")
        if default_deadline.endswith("d"):
            days = int(default_deadline[:-1])
            deadline_date = datetime.now() + timedelta(days=days)
        elif default_deadline.endswith("w"):
            weeks = int(default_deadline[:-1])
            deadline_date = datetime.now() + timedelta(weeks=weeks)
        else:
            # Default to 3 days if format is unrecognized
            deadline_date = datetime.now() + timedelta(days=3)

        return deadline_date.strftime("%Y-%m-%d")

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        """Update the status of a task."""
        # Find the task file across all domain folders
        task_file = None
        for domain, config in self.domains.items():
            folder = config["folder"]
            potential_file = os.path.join(folder, f"{task_id}.md")
            if os.path.exists(potential_file):
                task_file = potential_file
                break

        if not task_file:
            logger.error(f"Task {task_id} not found")
            return False

        # Read the current task file
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update the status field
        lines = content.split("\n")
        updated_lines = []
        for line in lines:
            if line.startswith("**Status:**"):
                updated_lines.append(f"**Status:** {new_status}")
            else:
                updated_lines.append(line)

        # Write back the updated content
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(updated_lines))

        logger.info(f"Updated task {task_id} status to {new_status}")
        return True

    def get_domain_summary(self, domain: str) -> Dict:
        """Get summary statistics for a specific domain."""
        if domain not in self.domains:
            raise ValueError(f"Unknown domain: {domain}")

        folder = self.domains[domain]["folder"]
        if not os.path.exists(folder):
            return {
                "domain": domain,
                "total_tasks": 0,
                "by_status": {},
                "by_priority": {}
            }

        # Count tasks by status and priority
        by_status = {}
        by_priority = {}
        total_tasks = 0

        for filename in os.listdir(folder):
            if filename.endswith(".md"):
                total_tasks += 1
                file_path = os.path.join(folder, filename)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract status and priority from the file
                status = "unknown"
                priority = "unknown"

                for line in content.split("\n"):
                    if line.startswith("**Status:**"):
                        status = line.split("**Status:**")[1].strip()
                    elif line.startswith("**Priority:**"):
                        priority = line.split("**Priority:**")[1].strip()

                by_status[status] = by_status.get(status, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "domain": domain,
            "total_tasks": total_tasks,
            "by_status": by_status,
            "by_priority": by_priority
        }

    def get_unified_summary(self) -> Dict:
        """Get a unified summary across all domains."""
        summary = {
            "created_at": datetime.now().isoformat(),
            "domains": {}
        }

        for domain in self.domains.keys():
            summary["domains"][domain] = self.get_domain_summary(domain)

        return summary

# Example usage
if __name__ == "__main__":
    # Initialize the Cross-Domain Manager
    cdm = CrossDomainManager()

    # Example: Create a task from raw data (simulating input from a watcher)
    raw_task_data = {
        "title": "Prepare Q1 Business Report",
        "content": "The client needs the Q1 business report asap. This is urgent and critical for the upcoming meeting with stakeholders.",
        "source": "gmail",
        "source_id": "email_12345",
        "assigned_to": "analyst_team",
        "tags": ["business", "report", "q1", "urgent"],
        "dependencies": ["data_collection", "market_analysis"]
    }

    task_file = cdm.create_task(raw_task_data)
    print(f"Created task: {task_file}")

    # Get domain summaries
    business_summary = cdm.get_domain_summary("business")
    print(f"Business summary: {business_summary}")

    personal_summary = cdm.get_domain_summary("personal")
    print(f"Personal summary: {personal_summary}")

    # Get unified summary
    unified_summary = cdm.get_unified_summary()
    print(f"Unified summary: {json.dumps(unified_summary, indent=2)}")