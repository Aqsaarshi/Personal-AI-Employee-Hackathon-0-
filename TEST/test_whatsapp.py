#!/usr/bin/env python3
"""
Test WhatsApp Watcher Script with Fake Data
Tests the message processing functionality without needing actual WhatsApp login
"""

import time
import os
import logging
from datetime import datetime

def setup_logging():
    """Setup logging to file"""
    log_dir = "Logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'whatsapp_test_log.md'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_needs_action_file(message_data):
    """Create a .md file in Needs_Action with message details"""
    needs_action_dir = "Needs_Action"
    if not os.path.exists(needs_action_dir):
        os.makedirs(needs_action_dir)

    filename = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(needs_action_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# WhatsApp Alert\n\n")
        f.write(f"**Contact:** {message_data['contact']}\n\n")
        f.write(f"**Time Received:** {message_data['time']}\n\n")
        f.write(f"**Message:**\n{message_data['message']}\n\n")
        f.write(f"**Keywords Detected:** {', '.join(message_data['keywords'])}\n\n")
        f.write("**Action Required:** Review and respond to this urgent message.\n")

    logging.info(f"Created alert for message from {message_data['contact']}")
    print(f"[OK] Created: {filepath}")

def check_whatsapp_messages(fake_messages):
    """Process fake messages with keywords"""
    keywords = ['urgent', 'invoice', 'asap', 'important', 'critical', 'emergency', 'need', 'help']
    
    processed_count = 0
    
    for msg in fake_messages:
        message_text = msg['message'].lower()
        
        # Check for keywords
        detected_keywords = []
        for keyword in keywords:
            if keyword.lower() in message_text:
                detected_keywords.append(keyword)

        if detected_keywords:
            message_data = {
                'contact': msg['contact'],
                'message': msg['message'],
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'keywords': detected_keywords
            }

            create_needs_action_file(message_data)
            processed_count += 1

    return processed_count

def main():
    """Main function with fake test data"""
    setup_logging()
    logging.info("Starting WhatsApp Watcher Test")
    print("=" * 50)
    print("WhatsApp Watcher - Test Mode (Fake Data)")
    print("=" * 50)

    # Fake test messages
    fake_messages = [
        {
            'contact': 'Ali Khan',
            'message': 'Hey, this is URGENT! I need your help with the invoice ASAP!'
        },
        {
            'contact': 'Sarah Ahmed',
            'message': 'Please review this important document when you get a chance.'
        },
        {
            'contact': 'Client Support',
            'message': 'Critical issue reported on production server. Emergency meeting needed.'
        },
        {
            'contact': 'Friend',
            'message': 'Hey! Are you coming to the party tonight?'
        },
        {
            'contact': 'Boss',
            'message': 'Need you to help with the presentation. It is very important!'
        }
    ]

    print(f"\nProcessing {len(fake_messages)} fake messages...\n")
    
    count = check_whatsapp_messages(fake_messages)
    
    print(f"\n[OK] Successfully processed {count} urgent messages")
    print(f"[OK] Check 'Needs_Action/' folder for generated files")
    
    logging.info(f"Test completed. Processed {count} messages")

if __name__ == "__main__":
    main()
