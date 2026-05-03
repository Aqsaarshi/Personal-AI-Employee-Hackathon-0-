const express = require('express');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());

// Configure transporter
const transporter = {
  sendMail: async (options) => {
    // Mock function for now - in production, we'd use the real transporter
    console.log('Mock email sent:', options);
    return { messageId: 'mock-id-' + Date.now() };
  }
};

// Function to log actions
const logAction = (message) => {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  const logPath = path.join(__dirname, '..', 'Logs', 'mcp_log.md');
  fs.appendFileSync(logPath, logEntry);
};

// MCP endpoint to handle commands
app.post('/mcp', async (req, res) => {
  const { command, args } = req.body;
  
  if (command === 'send_email') {
    const { to, subject, body } = args;
    
    try {
      // Validate required fields
      if (!to || !subject || !body) {
        logAction(`ERROR: Missing required fields for send_email command. Received: ${JSON.stringify({to: !!to, subject: !!subject, body: !!body})}`);
        return res.status(400).json({ 
          error: 'Missing required fields: to, subject, body' 
        });
      }
      
      // For now, just log the email action instead of actually sending
      logAction(`EMAIL DRAFT: To: ${to}, Subject: ${subject}, Body: ${body.substring(0, 100)}...`);
      
      // In a real implementation, we would send the email like this:
      /*
      const mailOptions = {
        from: process.env.GMAIL_USER,
        to,
        subject,
        text: body
      };
      
      const info = await transporter.sendMail(mailOptions);
      logAction(`Email sent successfully to ${to}. Message ID: ${info.messageId}`);
      */
      
      res.json({ 
        success: true, 
        message: `Email draft logged for: ${to}`,
        draft_info: { to, subject, body_preview: body.substring(0, 50) + '...' }
      });
    } catch (error) {
      logAction(`ERROR sending email to ${to}: ${error.message}`);
      res.status(500).json({ 
        error: `Failed to process send_email command: ${error.message}` 
      });
    }
  } else {
    logAction(`ERROR: Unknown command received: ${command}`);
    res.status(400).json({ 
      error: `Unknown command: ${command}` 
    });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  logAction(`Email MCP server listening on port ${PORT}`);
  console.log(`Email MCP server running on http://localhost:${PORT}`);
});