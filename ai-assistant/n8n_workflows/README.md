# N8N Workflow Examples

This directory contains example N8N workflows that integrate with the AI Assistant.

## Available Workflows

### 1. Task Automation (`task_automation.json`)

**Purpose**: Automates actions when tasks are created

**Features**:
- Receives webhook when a task is created
- Checks if the task is urgent
- Sends email notification for urgent tasks
- Can be extended to integrate with other services

**Webhook URL**: `http://localhost:5678/webhook/task-created`

**Trigger from Assistant**:
```bash
POST /api/v1/n8n/trigger
{
  "workflow_name": "task-created",
  "payload": {
    "data": {
      "title": "Important Task",
      "priority": "urgent",
      "due_date": "2025-11-11T10:00:00Z"
    }
  }
}
```

### 2. Email Automation (`email_automation.json`)

**Purpose**: Sends emails based on assistant commands

**Features**:
- Receives email request via webhook
- Supports bilingual responses (English/Urdu)
- Sends email using configured SMTP
- Returns success message in the requested language

**Webhook URL**: `http://localhost:5678/webhook/send-email`

**Trigger from Assistant**:
```bash
POST /api/v1/assistant
{
  "message": "Send email to john@example.com with subject 'Meeting' and say 'Let's meet tomorrow'",
  "language": "en"
}
```

## How to Import

1. Open N8N (usually at `http://localhost:5678`)
2. Click on **Workflows** in the left menu
3. Click **Import from File**
4. Select one of the JSON files from this directory
5. The workflow will be imported and ready to use

## Customization

### Email Configuration

For email workflows to work, you need to configure your SMTP settings in N8N:

1. Go to **Settings** > **Credentials**
2. Add a new **SMTP** credential
3. Enter your SMTP server details
4. Update the email nodes in the workflows to use your credentials

### Webhook URLs

The webhook URLs in these examples use `localhost:5678`. If your N8N instance runs on a different host/port, update:

1. The webhook nodes in the workflows
2. The `N8N_WEBHOOK_URL` in your `.env` file

## Creating Custom Workflows

You can create custom workflows for:

- **Calendar Integration**: Add events to Google Calendar or Outlook
- **File Monitoring**: Watch for file changes and trigger actions
- **Database Sync**: Sync tasks with external databases
- **Slack/Teams Notifications**: Send notifications to team channels
- **Browser Automation**: Automate web scraping or form filling
- **Data Processing**: Process CSV files, generate reports, etc.

## Testing Workflows

Use the N8N webhook testing feature:

1. Open the workflow in N8N
2. Click on the **Webhook** node
3. Copy the **Test URL**
4. Use curl or Postman to test:

```bash
curl -X POST http://localhost:5678/webhook-test/task-created \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task_created",
    "data": {
      "title": "Test Task",
      "priority": "high"
    }
  }'
```

## Integration with AI Assistant

The assistant automatically triggers N8N workflows when it detects relevant intents:

- **Task Created**: Triggers when a task is created
- **Email Request**: Triggers when the user asks to send an email
- **Custom Triggers**: You can add custom triggers in the NLP processor

## Troubleshooting

**Webhook not responding?**
- Check if N8N is running (`http://localhost:5678`)
- Verify the webhook URL in the workflow matches the configuration
- Check N8N logs for errors

**Email not sending?**
- Verify SMTP credentials are configured correctly
- Check if the email node has the correct credential selected
- Test SMTP connection in N8N settings

**Workflow not triggering?**
- Check the assistant logs for N8N integration errors
- Verify the workflow name matches in both the assistant and N8N
- Ensure the workflow is **activated** in N8N

## Additional Resources

- [N8N Documentation](https://docs.n8n.io/)
- [N8N Webhook Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [N8N Email Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.emailsend/)
