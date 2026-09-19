"""
AI Agent — receives user request, selects a tool, executes with optional approval.

Available tools:
- search_documents: RAG search over knowledge base
- classify_ticket: AI ticket classification
- summarize_document: Generate document summary
- generate_report: Create weekly report
- assign_ticket: Assign ticket (requires human approval)
- send_email: Send notification email (requires human approval)
"""

import logging
import re
import time
from django.utils import timezone

from ai.models import AgentRun, AgentApproval
from ai.services.rag import rag_answer
from ai.services.classifier import classify_ticket
from ai.services.summarizer import summarize_text
from ai.services.report_generator import generate_weekly_report
from ai.services.interaction_logger import log_interaction

logger = logging.getLogger('ai')

# Tools that modify data or send external messages need human approval
APPROVAL_REQUIRED_TOOLS = {'assign_ticket', 'send_email'}

TOOL_DESCRIPTIONS = {
    'search_documents': 'Search uploaded documents and answer questions (RAG)',
    'classify_ticket': 'Classify a support ticket by category, priority, department',
    'summarize_document': 'Generate a summary of document text',
    'generate_report': 'Generate a weekly operations report',
    'assign_ticket': 'Assign a ticket to a team member',
    'send_email': 'Send an email notification',
}


def _detect_tool(user_request: str) -> tuple[str, dict]:
    """
    Simple intent router — maps keywords in user request to a tool.
    In production this would be an LLM function-calling step.
    """
    req = user_request.lower()

    if any(w in req for w in ['assign', 'assign ticket', 'route ticket']):
        ticket_id = re.search(r'#?(\d+)', user_request)
        assignee = re.search(r'to\s+(\w+)', req)
        return 'assign_ticket', {
            'ticket_id': int(ticket_id.group(1)) if ticket_id else None,
            'assignee_username': assignee.group(1) if assignee else None,
        }

    if any(w in req for w in ['email', 'send mail', 'notify']):
        return 'send_email', {'message': user_request}

    if any(w in req for w in ['report', 'weekly', 'summary report']):
        return 'generate_report', {}

    if any(w in req for w in ['classify', 'category', 'priority ticket']):
        return 'classify_ticket', {'text': user_request}

    if any(w in req for w in ['summarize', 'summary of document']):
        return 'summarize_document', {'text': user_request}

    # Default: RAG document search
    return 'search_documents', {'question': user_request}


def _execute_tool(tool: str, tool_input: dict, user) -> dict:
    """Run the selected tool and return its output."""
    if tool == 'search_documents':
        question = tool_input.get('question', '')
        return rag_answer(user, question)

    if tool == 'classify_ticket':
        text = tool_input.get('text', '')
        return classify_ticket('Agent Request', text, user=user)

    if tool == 'summarize_document':
        text = tool_input.get('text', '')
        return summarize_text(text, title='Agent Summary', user=user)

    if tool == 'generate_report':
        return generate_weekly_report(user)

    if tool == 'assign_ticket':
        return {
            'action': 'assign_ticket',
            'ticket_id': tool_input.get('ticket_id'),
            'assignee': tool_input.get('assignee_username'),
            'message': 'Pending human approval before assignment.',
        }

    if tool == 'send_email':
        return {
            'action': 'send_email',
            'message': tool_input.get('message'),
            'status': 'Pending human approval before sending.',
        }

    return {'error': f'Unknown tool: {tool}'}


def run_agent(user, user_request: str) -> AgentRun:
    """
    Main agent entry point:
    1. Detect tool from user request
    2. If sensitive → create approval record, pause
    3. Else → execute immediately and store result
    """
    start = time.time()
    tool, tool_input = _detect_tool(user_request)

    agent_run = AgentRun.objects.create(
        user=user,
        user_request=user_request,
        selected_tool=tool,
        tool_input=tool_input,
        status='RUNNING',
        requires_approval=tool in APPROVAL_REQUIRED_TOOLS,
    )

    if tool in APPROVAL_REQUIRED_TOOLS:
        action_desc = (
            f"Agent wants to run '{tool}' with input: {tool_input}. "
            f"Please approve or reject this action."
        )
        AgentApproval.objects.create(
            agent_run=agent_run,
            action_description=action_desc,
        )
        agent_run.status = 'AWAITING_APPROVAL'
        agent_run.save(update_fields=['status'])
    else:
        output = _execute_tool(tool, tool_input, user)
        agent_run.tool_output = output
        agent_run.final_answer = _format_agent_answer(tool, output)
        agent_run.status = 'COMPLETED'
        agent_run.completed_at = timezone.now()
        agent_run.save()

    duration_ms = int((time.time() - start) * 1000)
    log_interaction(
        user=user,
        interaction_type='AGENT_RUN',
        input_data={'request': user_request, 'tool': tool},
        output_data={'status': agent_run.status, 'tool_output': agent_run.tool_output},
        duration_ms=duration_ms,
    )
    return agent_run


def approve_agent_action(agent_run: AgentRun, user, approved: bool) -> AgentRun:
    """
    Human approves or rejects a pending agent action, then executes if approved.
    """
    approval = agent_run.approval
    approval.decision = 'APPROVED' if approved else 'REJECTED'
    approval.decided_by = user
    approval.decided_at = timezone.now()
    approval.save()

    if not approved:
        agent_run.status = 'REJECTED'
        agent_run.final_answer = 'Action was rejected by a human reviewer.'
        agent_run.completed_at = timezone.now()
        agent_run.save()
        return agent_run

    # Execute the approved action
    tool = agent_run.selected_tool
    output = _execute_tool(tool, agent_run.tool_input, user)

    if tool == 'assign_ticket':
        output = _do_assign_ticket(agent_run.tool_input, user)
    elif tool == 'send_email':
        output = _do_send_email(agent_run.tool_input, user)

    agent_run.tool_output = output
    agent_run.final_answer = _format_agent_answer(tool, output)
    agent_run.status = 'COMPLETED'
    agent_run.completed_at = timezone.now()
    agent_run.save()
    return agent_run


def _do_assign_ticket(tool_input: dict, user) -> dict:
    """Actually assign a ticket after approval."""
    from tickets.models import Ticket
    from users.models import CustomUser

    ticket_id = tool_input.get('ticket_id')
    username = tool_input.get('assignee_username')
    if not ticket_id:
        return {'error': 'No ticket ID provided'}

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        assignee = CustomUser.objects.filter(username=username).first() if username else None
        if assignee:
            ticket.assigned_to = assignee
            ticket.save(update_fields=['assigned_to', 'updated_at'])
            return {'success': True, 'message': f'Ticket #{ticket_id} assigned to {username}'}
        return {'error': f'User {username} not found'}
    except Ticket.DoesNotExist:
        return {'error': f'Ticket #{ticket_id} not found'}


def _do_send_email(tool_input: dict, user) -> dict:
    """Send email via Django mail backend after approval."""
    from django.core.mail import send_mail
    from django.conf import settings

    message = tool_input.get('message', 'Agent notification')
    recipient = getattr(user, 'email', None) or 'admin@example.com'
    try:
        send_mail(
            subject='AI Agent Notification',
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@aiops.local'),
            recipient_list=[recipient],
            fail_silently=False,
        )
        return {'success': True, 'message': f'Email sent to {recipient}'}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


def _format_agent_answer(tool: str, output: dict) -> str:
    """Turn tool output into a readable final answer for the user."""
    if tool == 'search_documents':
        return output.get('answer', 'No answer generated.')
    if tool == 'classify_ticket':
        return (
            f"Category: {output.get('ai_category')}, "
            f"Priority: {output.get('ai_priority')}, "
            f"Department: {output.get('ai_department')} "
            f"(confidence: {output.get('ai_confidence')})"
        )
    if tool == 'summarize_document':
        return output.get('summary', '')
    if tool == 'generate_report':
        return output.get('content', '')[:2000]
    if 'message' in output:
        return output['message']
    if 'error' in output:
        return f"Error: {output['error']}"
    return str(output)
