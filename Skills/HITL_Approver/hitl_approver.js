const fs = require('fs');
const path = require('path');

/**
 * HITL Approver Skill
 * Creates approval files for sensitive actions
 */

class HITLApprover {
  constructor() {
    this.pendingApprovalDir = path.join(__dirname, '../../Pending_Approval');
    this.approvedDir = path.join(__dirname, '../../Approved');
    this.rejectedDir = path.join(__dirname, '../../Rejected');
    this.doneDir = path.join(__dirname, '../../Done');
  }

  /**
   * Creates an approval file for a sensitive action
   * @param {string} action - The type of action (e.g., 'email', 'post')
   * @param {Object} details - Details about the action
   * @returns {Promise<string>} Path to the created approval file
   */
  async createApproval(action, details) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${action}_approval_${timestamp}.md`;
    const filePath = path.join(this.pendingApprovalDir, fileName);

    // Create YAML frontmatter with action details
    const yamlFrontmatter = `---
type: ${action}
details:
  to: ${details.to || ''}
  subject: ${details.subject || ''}
  body: ${details.body || ''}
  timestamp: ${new Date().toISOString()}
  status: pending
---

# ${action.charAt(0).toUpperCase() + action.slice(1)} Approval Request

## Action Details
- **Type**: ${action}
- **To**: ${details.to || 'N/A'}
- **Subject**: ${details.subject || 'N/A'}
- **Body Preview**: ${details.body ? details.body.substring(0, 100) + (details.body.length > 100 ? '...' : '') : 'N/A'}

## Instructions
Review this ${action} request and move this file to:
- **Approved/** folder to approve the action
- **Rejected/** folder to reject the action

The system will automatically process the action based on the folder location.
`;

    // Write the approval file
    await fs.promises.writeFile(filePath, yamlFrontmatter);
    
    console.log(`Created approval file: ${filePath}`);
    return filePath;
  }

  /**
   * Checks if an action has been approved or rejected
   * @param {string} approvalFilePath - Path to the approval file
   * @returns {Object} Status object with approved/rejected status and reason
   */
  async checkApprovalStatus(approvalFilePath) {
    const fileName = path.basename(approvalFilePath);
    
    // Check if file exists in Approved directory
    const approvedPath = path.join(this.approvedDir, fileName);
    if (fs.existsSync(approvedPath)) {
      return { approved: true, path: approvedPath, reason: 'Manually approved by human' };
    }
    
    // Check if file exists in Rejected directory
    const rejectedPath = path.join(this.rejectedDir, fileName);
    if (fs.existsSync(rejectedPath)) {
      return { approved: false, path: rejectedPath, reason: 'Manually rejected by human' };
    }
    
    // Still pending
    return { approved: null, path: approvalFilePath, reason: 'Still pending approval' };
  }

  /**
   * Moves an approved file to the Done directory after processing
   * @param {string} approvalFilePath - Path to the approved file
   */
  async moveToDone(approvalFilePath) {
    const fileName = path.basename(approvalFilePath);
    const donePath = path.join(this.doneDir, fileName);
    
    // Move the file to Done directory
    await fs.promises.rename(approvalFilePath, donePath);
    console.log(`Moved approved file to Done: ${donePath}`);
  }

  /**
   * Moves a rejected file to the Done directory after processing
   * @param {string} approvalFilePath - Path to the rejected file
   */
  async moveToDoneRejected(approvalFilePath) {
    const fileName = path.basename(approvalFilePath);
    const donePath = path.join(this.doneDir, `rejected_${fileName}`);
    
    // Move the file to Done directory with rejected prefix
    await fs.promises.rename(approvalFilePath, donePath);
    console.log(`Moved rejected file to Done: ${donePath}`);
  }
}

module.exports = HITLApprover;