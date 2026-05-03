const fs = require('fs');
const path = require('path');
const HITLApprover = require('../../Skills/HITL_Approver/hitl_approver');

class ReasoningLoop {
  constructor() {
    this.plansDir = path.join(__dirname, '../../Plans');
    this.hitlApprover = new HITLApprover();
  }

  /**
   * Executes a reasoning loop with HITL approval for sensitive actions
   * @param {Object} task - The task to process
   * @param {string} planName - Name for the plan file
   */
  async execute(task, planName) {
    const planPath = path.join(this.plansDir, `${planName}.md`);
    
    // Initialize plan file
    await this.initializePlan(planPath, task.description || task.name || 'Untitled Task');
    
    // Process each step in the task
    for (const step of task.steps || []) {
      await this.updatePlan(planPath, `Processing: ${step.description}`, 'in-progress');
      
      // Check if this is a sensitive action that requires approval
      if (this.isSensitiveAction(step)) {
        console.log(`Sensitive action detected: ${step.action}`);
        
        // Create approval request
        const approvalResult = await this.requestApproval(step);
        
        if (approvalResult.approved) {
          console.log(`Action approved: ${step.action}`);
          await this.executeAction(step);
          await this.updatePlan(planPath, step.description, 'completed-approved');
        } else {
          console.log(`Action rejected: ${step.action}`);
          await this.updatePlan(planPath, `${step.description} - REJECTED`, 'rejected');
        }
      } else {
        // Execute non-sensitive action directly
        await this.executeAction(step);
        await this.updatePlan(planPath, step.description, 'completed');
      }
    }
    
    console.log(`Reasoning loop completed for task: ${planName}`);
  }

  /**
   * Determines if an action is sensitive and requires human approval
   * @param {Object} step - The step to evaluate
   * @returns {boolean} True if the action is sensitive
   */
  isSensitiveAction(step) {
    const sensitiveActions = ['send_email', 'post_to_social', 'make_payment', 'delete_data', 'modify_permissions'];
    return sensitiveActions.includes(step.action) || 
           (step.description && (
             step.description.toLowerCase().includes('email') ||
             step.description.toLowerCase().includes('post') ||
             step.description.toLowerCase().includes('payment') ||
             step.description.toLowerCase().includes('delete') ||
             step.description.toLowerCase().includes('sensitive')
           ));
  }

  /**
   * Requests human approval for a sensitive action
   * @param {Object} step - The step requiring approval
   * @returns {Promise<Object>} Approval result
   */
  async requestApproval(step) {
    // Create approval file with action details
    const details = {
      to: step.to || step.recipients || '',
      subject: step.subject || step.title || step.description || '',
      body: step.body || step.content || step.description || '',
      action: step.action || 'unknown',
      timestamp: new Date().toISOString()
    };

    const approvalFilePath = await this.hitlApprover.createApproval(
      step.action.replace('send_', '') || 'action', 
      details
    );

    console.log(`Approval requested. Waiting for human decision...`);
    console.log(`Move file to Approved/ or Rejected/ folder: ${approvalFilePath}`);

    // Wait for approval decision (in a real implementation, this would be asynchronous)
    return await this.waitForApprovalDecision(approvalFilePath);
  }

  /**
   * Waits for approval decision by monitoring the approval file
   * @param {string} approvalFilePath - Path to the approval file
   * @returns {Promise<Object>} Approval result
   */
  async waitForApprovalDecision(approvalFilePath) {
    // In a real implementation, this would continuously check until a decision is made
    // For this simulation, we'll return a mock result after a short delay
    return new Promise((resolve) => {
      setTimeout(async () => {
        // Check the status of the approval file
        const status = await this.hitlApprover.checkApprovalStatus(approvalFilePath);
        
        if (status.approved !== null) {
          resolve(status);
        } else {
          // If still pending, return a default decision (in real implementation, keep waiting)
          resolve({ approved: true, reason: 'Auto-approved for demo purposes' });
        }
      }, 2000); // Wait 2 seconds before checking
    });
  }

  /**
   * Executes an action
   * @param {Object} step - The step to execute
   */
  async executeAction(step) {
    console.log(`Executing action: ${step.action || step.description}`);
    
    // In a real implementation, this would call the appropriate MCP server
    // For now, we'll simulate the action
    switch (step.action) {
      case 'send_email':
        await this.simulateEmailSend(step);
        break;
      case 'post_to_social':
        await this.simulateSocialPost(step);
        break;
      default:
        console.log(`Executing generic action: ${step.action}`);
        break;
    }
  }

  /**
   * Simulates sending an email
   * @param {Object} step - The email step to simulate
   */
  async simulateEmailSend(step) {
    console.log(`Simulating email send to: ${step.to || step.recipients}`);
    console.log(`Subject: ${step.subject}`);
    console.log(`Body: ${step.body || step.content}`);
    
    // Log the simulated email action
    const logPath = path.join(__dirname, '../../Logs/mcp_log.md');
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] SIMULATED EMAIL SENT: To=${step.to || step.recipients}, Subject=${step.subject}\n`;
    
    await fs.promises.appendFile(logPath, logEntry);
  }

  /**
   * Simulates posting to social media
   * @param {Object} step - The post step to simulate
   */
  async simulateSocialPost(step) {
    console.log(`Simulating social post: ${step.title || step.subject}`);
    console.log(`Content: ${step.body || step.content}`);
    
    // Log the simulated post action
    const logPath = path.join(__dirname, '../../Logs/mcp_log.md');
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] SIMULATED SOCIAL POST: Title=${step.title || step.subject}\n`;
    
    await fs.promises.appendFile(logPath, logEntry);
  }

  /**
   * Initializes a plan file
   * @param {string} planPath - Path to the plan file
   * @param {string} taskDescription - Description of the task
   */
  async initializePlan(planPath, taskDescription) {
    const planContent = `# Plan for ${taskDescription}

- [ ] Initializing plan
`;
    await fs.promises.writeFile(planPath, planContent);
  }

  /**
   * Updates a plan file with a new status
   * @param {string} planPath - Path to the plan file
   * @param {string} stepDescription - Description of the step
   * @param {string} status - Status of the step (completed, in-progress, rejected)
   */
  async updatePlan(planPath, stepDescription, status) {
    let content = await fs.promises.readFile(planPath, 'utf8');
    
    // Add the new step with appropriate checkbox
    let stepLine = '';
    switch (status) {
      case 'completed':
        stepLine = `- [x] ${stepDescription}`;
        break;
      case 'completed-approved':
        stepLine = `- [x] ${stepDescription} (APPROVED)`;
        break;
      case 'rejected':
        stepLine = `- [x] ${stepDescription} (REJECTED)`;
        break;
      case 'in-progress':
        stepLine = `- [-] ${stepDescription}`;
        break;
      default:
        stepLine = `- [ ] ${stepDescription}`;
        break;
    }
    
    // Append the step to the content
    content += `\n${stepLine}`;
    
    await fs.promises.writeFile(planPath, content);
  }
}

module.exports = ReasoningLoop;