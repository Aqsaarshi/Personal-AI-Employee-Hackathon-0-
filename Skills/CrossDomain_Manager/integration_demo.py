"""
Integration script for Cross-Domain Manager
Demonstrates how watcher scripts can interface with the Cross-Domain Manager
"""
import json
import os
import sys
from datetime import datetime

# Add the project root to the path so we can import from Skills
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.CrossDomain_Manager.crossdomain_manager import CrossDomainManager

def process_watcher_data(watcher_name, raw_data):
    """
    Process data from any watcher and route it to Cross-Domain Manager
    """
    print(f"Processing {watcher_name} data through Cross-Domain Manager...")

    # Initialize the Cross-Domain Manager
    cdm = CrossDomainManager()

    # Format the raw data as needed by the Cross-Domain Manager
    formatted_data = {
        "title": raw_data.get("title", "Untitled Task from " + watcher_name),
        "content": raw_data.get("content", ""),
        "source": watcher_name,
        "source_id": raw_data.get("id", f"{watcher_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        "assigned_to": raw_data.get("assigned_to", "unassigned"),
        "tags": raw_data.get("tags", []),
        "dependencies": raw_data.get("dependencies", [])
    }

    # Create the task using Cross-Domain Manager
    task_file = cdm.create_task(formatted_data)
    print(f"Created task file: {task_file}")

    return task_file

def simulate_watcher_integrations():
    """
    Simulate integration with different watcher scripts
    """
    print("Simulating Cross-Domain Manager integration with watchers...\n")

    # Simulate Gmail Watcher data
    gmail_data = {
        "title": "Client Meeting Follow-up Required",
        "content": "Important client meeting scheduled for tomorrow. Need to prepare agenda and review contract details. This is urgent and critical for business relationship.",
        "id": "gmail_msg_12345",
        "assigned_to": "account_manager",
        "tags": ["business", "meeting", "urgent", "client"],
        "dependencies": ["review_contract", "prepare_agenda"]
    }

    print("1. Processing Gmail Watcher data:")
    process_watcher_data("gmail", gmail_data)
    print()

    # Simulate LinkedIn Watcher data
    linkedin_data = {
        "title": "Post Engagement Response Needed",
        "content": "Our latest LinkedIn post about digital transformation has received high engagement. Need to respond to comments and follow up with interested prospects. This is important for business development.",
        "id": "linkedin_post_67890",
        "assigned_to": "marketing_team",
        "tags": ["business", "social_media", "engagement", "marketing"],
        "dependencies": ["review_comments", "follow_up_prospects"]
    }

    print("2. Processing LinkedIn Watcher data:")
    process_watcher_data("linkedin", linkedin_data)
    print()

    # Simulate WhatsApp Watcher data
    whatsapp_data = {
        "title": "Family Dinner Planning",
        "content": "Family dinner scheduled for this weekend. Need to coordinate with family members and make restaurant reservation. This is a personal commitment.",
        "id": "whatsapp_grp_54321",
        "assigned_to": "personal",
        "tags": ["personal", "family", "dinner", "planning"],
        "dependencies": ["confirm_attendees", "book_restaurant"]
    }

    print("3. Processing WhatsApp Watcher data:")
    process_watcher_data("whatsapp", whatsapp_data)
    print()

    # Simulate Vault Watcher data
    vault_data = {
        "title": "Project Deadline Review",
        "content": "Monthly project deadline review meeting. Need to prepare status reports for all ongoing projects. This is important for team alignment.",
        "id": "vault_file_98765",
        "assigned_to": "project_manager",
        "tags": ["business", "meeting", "project", "deadline", "important"],
        "dependencies": ["gather_status_reports", "prepare_presentation"]
    }

    print("4. Processing Vault Watcher data:")
    process_watcher_data("vault", vault_data)
    print()

    # Initialize Cross-Domain Manager to show summary
    cdm = CrossDomainManager()

    print("5. Getting domain summaries:")
    business_summary = cdm.get_domain_summary("business")
    print(f"Business domain summary: {json.dumps(business_summary, indent=2)}")

    personal_summary = cdm.get_domain_summary("personal")
    print(f"Personal domain summary: {json.dumps(personal_summary, indent=2)}")

    unified_summary = cdm.get_unified_summary()
    print(f"Unified summary: {json.dumps(unified_summary, indent=2)}")

if __name__ == "__main__":
    simulate_watcher_integrations()