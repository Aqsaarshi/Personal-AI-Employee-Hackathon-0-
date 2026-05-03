// Simple test for the email MCP server
const fs = require('fs');
const path = require('path');

// Function to log actions (same as in email_mcp.js)
const logAction = (message) => {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  const logPath = path.join(__dirname, '..', 'Logs', 'mcp_log.md');
  fs.appendFileSync(logPath, logEntry);
  console.log(logEntry.trim());
};

console.log('Testing email MCP functionality...');

// Simulate the send_email command processing
const command = 'send_email';
const args = {
  to: 'test@example.com',
  subject: 'Test Subject',
  body: 'This is a test email body for the MCP server.'
};

if (command === 'send_email') {
  const { to, subject, body } = args;
  
  // Validate required fields
  if (!to || !subject || !body) {
    logAction(`ERROR: Missing required fields for send_email command. Received: ${JSON.stringify({to: !!to, subject: !!subject, body: !!body})}`);
    console.log('Error: Missing required fields');
  } else {
    // Log the email action (as the server would)
    logAction(`EMAIL DRAFT: To: ${to}, Subject: ${subject}, Body: ${body.substring(0, 100)}...`);
    
    console.log('Success: Email draft logged');
    console.log(JSON.stringify({ 
      success: true, 
      message: `Email draft logged for: ${to}`,
      draft_info: { to, subject, body_preview: body.substring(0, 50) + '...' }
    }, null, 2));
  }
}

console.log('\nCheck the Logs/mcp_log.md file to see the logged entry.');