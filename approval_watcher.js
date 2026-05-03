const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const HITLApprover = require('./Skills/HITL_Approver/hitl_approver.js');

class ApprovalWatcher {
  constructor() {
    this.hitlApprover = new HITLApprover();
    this.approvedDir = path.join(__dirname, 'Approved');
    this.rejectedDir = path.join(__dirname, 'Rejected');
    this.watcher = null;
    this.processingQueue = new Set(); // To prevent duplicate processing
  }

  /**
   * Starts watching the approval directories
   */
  startWatching() {
    console.log('Starting approval watcher...');
    
    // Watch both Approved and Rejected directories
    this.watchDirectory(this.approvedDir, 'approved');
    this.watchDirectory(this.rejectedDir, 'rejected');
  }

  /**
   * Watches a specific directory for file changes
   * @param {string} dirPath - Directory to watch
   * @param {string} type - Type of directory ('approved' or 'rejected')
   */
  watchDirectory(dirPath, type) {
    if (!fs.existsSync(dirPath)) {
      console.error(`Directory does not exist: ${dirPath}`);
      return;
    }

    this.watcher = fs.watch(dirPath, (eventType, filename) => {
      if (filename && (filename.endsWith('.md') || filename.endsWith('.txt'))) {
        console.log(`${eventType} event detected in ${type} directory for file: ${filename}`);
        
        if (eventType === 'rename') { // File added/removed
          const filePath = path.join(dirPath, filename);
          
          // Add a small delay to ensure file is completely written
          setTimeout(() => {
            this.handleFileChange(filePath, type);
          }, 1000);
        }
      }
    });

    console.log(`Now watching ${dirPath} for ${type} files...`);
  }

  /**
   * Handles file changes in the watched directories
   * @param {string} filePath - Path to the changed file
   * @param {string} type - Type of directory ('approved' or 'rejected')
   */
  async handleFileChange(filePath, type) {
    // Prevent duplicate processing
    if (this.processingQueue.has(filePath)) {
      return;
    }
    
    this.processingQueue.add(filePath);
    
    try {
      console.log(`Processing ${type} file: ${filePath}`);
      
      if (type === 'approved') {
        await this.processApprovedFile(filePath);
      } else if (type === 'rejected') {
        await this.processRejectedFile(filePath);
      }
    } catch (error) {
      console.error(`Error processing ${type} file ${filePath}:`, error);
    } finally {
      // Remove from queue after processing
      this.processingQueue.delete(filePath);
    }
  }

  /**
   * Process an approved file by executing the corresponding action
   * @param {string} filePath - Path to the approved file
   */
  async processApprovedFile(filePath) {
    try {
      const content = await fs.promises.readFile(filePath, 'utf8');
      
      // Extract action details from YAML frontmatter
      const yamlMatch = content.match(/---\n([\s\S]*?)\n---/);
      if (!yamlMatch) {
        console.error('No YAML frontmatter found in approved file');
        return;
      }
      
      const yamlContent = yamlMatch[1];
      const yamlLines = yamlContent.split('\n');
      
      let actionType = '';
      let actionDetails = {};
      
      for (const line of yamlLines) {
        if (line.startsWith('type:')) {
          actionType = line.replace('type:', '').trim();
        } else if (line.includes('details:')) {
          // Parse details section
          continue; // Skip the details header line
        } else if (line.trim().startsWith('to:') && actionDetails.to === undefined) {
          actionDetails.to = line.replace('to:', '').trim();
        } else if (line.trim().startsWith('subject:') && actionDetails.subject === undefined) {
          actionDetails.subject = line.replace('subject:', '').trim();
        } else if (line.trim().startsWith('body:') && actionDetails.body === undefined) {
          actionDetails.body = line.replace('body:', '').trim();
        }
      }
      
      console.log(`Executing approved ${actionType} action:`, actionDetails);
      
      // Execute the action via MCP if it's an email
      if (actionType === 'email') {
        await this.executeEmailViaMCP(actionDetails);
      } else if (actionType === 'post') {
        await this.executePostViaMCP(actionDetails);
      } else {
        console.log(`Unknown action type: ${actionType}`);
      }
      
      // Move the file to Done directory after processing
      await this.hitlApprover.moveToDone(filePath);
      
    } catch (error) {
      console.error('Error processing approved file:', error);
    }
  }

  /**
   * Process a rejected file by logging and moving to Done
   * @param {string} filePath - Path to the rejected file
   */
  async processRejectedFile(filePath) {
    try {
      const content = await fs.promises.readFile(filePath, 'utf8');
      
      // Extract action details from YAML frontmatter
      const yamlMatch = content.match(/---\n([\s\S]*?)\n---/);
      if (yamlMatch) {
        const yamlContent = yamlMatch[1];
        console.log('Rejected action details:', yamlContent);
      }
      
      console.log(`Action rejected: ${filePath}`);
      
      // Log rejection
      const logPath = path.join(__dirname, 'Logs', 'rejection_log.md');
      const timestamp = new Date().toISOString();
      const logEntry = `[${timestamp}] Action rejected: ${filePath}\n`;
      
      if (!fs.existsSync(path.dirname(logPath))) {
        fs.mkdirSync(path.dirname(logPath), { recursive: true });
      }
      
      await fs.promises.appendFile(logPath, logEntry);
      
      // Move the file to Done directory after processing
      await this.hitlApprover.moveToDoneRejected(filePath);
      
    } catch (error) {
      console.error('Error processing rejected file:', error);
    }
  }

  /**
   * Execute email action via MCP server
   * @param {Object} details - Email details
   */
  async executeEmailViaMCP(details) {
    try {
      // In a real implementation, this would call the MCP server
      // For now, we'll simulate the call
      console.log(`Simulating email send via MCP:`, details);
      
      // Log the action
      const logPath = path.join(__dirname, 'Logs', 'mcp_log.md');
      const timestamp = new Date().toISOString();
      const logEntry = `[${timestamp}] Email sent via MCP: To=${details.to}, Subject=${details.subject}\n`;
      
      if (!fs.existsSync(path.dirname(logPath))) {
        fs.mkdirSync(path.dirname(logPath), { recursive: true });
      }
      
      await fs.promises.appendFile(logPath, logEntry);
      
      console.log('Email action executed successfully');
    } catch (error) {
      console.error('Error executing email via MCP:', error);
    }
  }

  /**
   * Execute post action via MCP server
   * @param {Object} details - Post details
   */
  async executePostViaMCP(details) {
    try {
      // In a real implementation, this would call the MCP server
      // For now, we'll simulate the call
      console.log(`Simulating post creation via MCP:`, details);
      
      // Log the action
      const logPath = path.join(__dirname, 'Logs', 'mcp_log.md');
      const timestamp = new Date().toISOString();
      const logEntry = `[${timestamp}] Post created via MCP: Subject=${details.subject}\n`;
      
      if (!fs.existsSync(path.dirname(logPath))) {
        fs.mkdirSync(path.dirname(logPath), { recursive: true });
      }
      
      await fs.promises.appendFile(logPath, logEntry);
      
      console.log('Post action executed successfully');
    } catch (error) {
      console.error('Error executing post via MCP:', error);
    }
  }

  /**
   * Stops watching the directories
   */
  stopWatching() {
    if (this.watcher) {
      this.watcher.close();
      console.log('Stopped approval watcher');
    }
  }
}

// If this file is run directly, start the watcher
if (require.main === module) {
  const watcher = new ApprovalWatcher();
  watcher.startWatching();
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nStopping approval watcher...');
    watcher.stopWatching();
    process.exit(0);
  });
}

module.exports = ApprovalWatcher;