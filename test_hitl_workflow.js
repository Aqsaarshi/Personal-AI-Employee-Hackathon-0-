const ReasoningLoop = require('./Skills/Reasoning_Loop/reasoning_loop');
const HITLApprover = require('./Skills/HITL_Approver/hitl_approver');
const fs = require('fs');
const path = require('path');

async function testHITLWorkflow() {
  console.log('=== Testing HITL Workflow with Fake Email ===\n');
  
  // Create an instance of the HITL Approver
  const hitlApprover = new HITLApprover();
  
  // Define a test task with a sensitive action (sending email)
  const testTask = {
    name: 'Test Email Send Task',
    description: 'Test task to send an email via HITL workflow',
    steps: [
      {
        action: 'send_email',
        description: 'Send welcome email to new customer',
        to: 'customer@example.com',
        subject: 'Welcome to our service!',
        body: 'Dear customer, thank you for joining our service. We hope you enjoy using our platform.'
      },
      {
        action: 'log_activity',
        description: 'Log the email activity'
      }
    ]
  };
  
  console.log('Step 1: Creating approval request for sensitive action...\n');
  
  // Create approval for the email action
  const details = {
    to: testTask.steps[0].to,
    subject: testTask.steps[0].subject,
    body: testTask.steps[0].body
  };
  
  const approvalFilePath = await hitlApprover.createApproval('email', details);
  console.log(`✓ Approval file created: ${approvalFilePath}\n`);
  
  console.log('Step 2: Simulating human approval process...\n');
  console.log('INSTRUCTIONS FOR USER:');
  console.log('- Move the approval file to the "Approved" folder to approve the action');
  console.log('- Move the approval file to the "Rejected" folder to reject the action\n');
  
  // Show the content of the approval file
  const approvalContent = await fs.promises.readFile(approvalFilePath, 'utf8');
  console.log('APPROVAL FILE CONTENT:');
  console.log(approvalContent);
  console.log('');
  
  console.log('Step 3: Starting approval watcher to monitor for decisions...\n');
  
  // Start the approval watcher in the background
  const ApprovalWatcher = require('./approval_watcher');
  const watcher = new ApprovalWatcher();
  watcher.startWatching();
  
  console.log('Approval watcher started. Monitoring Approved/ and Rejected/ folders...\n');
  
  console.log('Step 4: Simulating reasoning loop with HITL integration...\n');
  
  // Create and execute a reasoning loop with the test task
  const reasoningLoop = new ReasoningLoop();
  await reasoningLoop.execute(testTask, 'test_hitl_workflow');
  
  console.log('\nStep 5: Verifying logs...\n');
  
  // Check the logs to see if the action was processed
  const logPath = path.join(__dirname, 'Logs', 'mcp_log.md');
  if (await fs.promises.access(logPath).then(() => true).catch(() => false)) {
    const logContent = await fs.promises.readFile(logPath, 'utf8');
    console.log('Current log content:');
    console.log(logContent);
  } else {
    console.log('Log file does not exist yet.');
  }
  
  console.log('\nTest completed. Remember to move the approval file to the appropriate folder (Approved/ or Rejected/) to see the full workflow in action.');
  console.log('The approval watcher will process the file once moved to the correct folder.');
}

// Run the test
testHITLWorkflow().catch(console.error);