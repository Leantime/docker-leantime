"""
Leantime MCP server — FastMCP (Python) implementation.

Mirrors the Node.js leantime-mcp server exactly.
Connects to Leantime via JSON-RPC at {LEANTIME_BASE_URL}/api/jsonrpc.

Environment variables:
    LEANTIME_BASE_URL  Base URL for Leantime instance (default: http://localhost:8090)
    LEANTIME_API_KEY   API key from Leantime Settings → API (required)
"""

import json
import os
from datetime import date
from typing import Optional

import httpx
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP("leantime-mcp")

# ---------------------------------------------------------------------------
# JSON-RPC helper
# ---------------------------------------------------------------------------

_request_id = 0


async def rpc(method: str, params: dict = None) -> object:
    """
    Call a Leantime JSON-RPC method.

    Args:
        method: Fully-qualified RPC method, e.g. "leantime.rpc.Projects.Projects.getAll"
        params: Named parameters dict for the method (may be empty).

    Returns:
        The ``result`` field from the JSON-RPC response.

    Raises:
        RuntimeError: When the API key is missing, HTTP request fails,
                      or the server returns a JSON-RPC error.
    """
    global _request_id

    base_url = os.environ.get("LEANTIME_BASE_URL", "http://192.168.2.48:8080").strip()
    api_key = os.environ.get("LEANTIME_API_KEY", "lt_scXGZxob1bCyw99zwypjJ4vx5F94ehSJ_mcYS8SuAC641d9lwiVaJZm3UklMPeGFz").strip()

    if not api_key:
        raise RuntimeError(
            "LEANTIME_API_KEY environment variable is not set. "
            "Create an API key in Leantime under Settings → API and set it as LEANTIME_API_KEY."
        )

    _request_id += 1

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": _request_id,
    }

    print(f"[rpc] {method} → {base_url} | key={api_key[:8]}...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/jsonrpc",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
            },
            content=json.dumps(payload),
        )

    if response.is_error:
        raise RuntimeError(f"HTTP {response.status_code}: {response.reason_phrase}")

    data = response.json()

    if "error" in data and data["error"]:
        error = data["error"]
        detail = f" — {error['data']}" if error.get("data") else ""
        raise RuntimeError(f"Leantime error: {error.get('message', 'unknown')}{detail}")

    return data.get("result")


def _fmt(data: object) -> str:
    """Serialize an RPC result to a pretty-printed JSON string."""
    if data is None:
        return "No data returned."
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_projects(status: str = "open") -> str:
    """
    List all projects available to the current user.
    Returns project IDs, names, statuses and descriptions.

    Args:
        status: Filter by project status — "open" (default), "closed", or "all".
    """
    result = await rpc(
        "leantime.rpc.Projects.Projects.getAll",
        {"showClosedProjects": status in ("closed", "all")},
    )
    if not result:
        return "No projects found."
    return _fmt(result)


@mcp.tool()
async def get_project(project_id: int) -> str:
    """
    Get full details of a specific project by its ID.

    Args:
        project_id: The numeric project ID.
    """
    result = await rpc(
        "leantime.rpc.Projects.Projects.getProject",
        {"id": project_id},
    )
    if not result:
        return f"Project {project_id} not found."
    return _fmt(result)


@mcp.tool()
async def create_project(
    name: str,
    details: str = "",
    client_id: int = 0,
    status: str = "open",
) -> str:
    """
    Create a new project.

    Args:
        name:      Project name (required).
        details:   Project description.
        client_id: Optional client ID to associate the project with.
        status:    Project status — "open" (default) or "closed".
    """
    values = {
        "name": name,
        "details": details,
        "clientId": client_id,
        "status": status,
        "projectType": "project",
    }
    result = await rpc(
        "leantime.rpc.Projects.Projects.addProject",
        {"values": values},
    )
    if not result:
        return "Failed to create project."
    return f"Project created successfully with ID: {result}"


@mcp.tool()
async def update_project(
    project_id: int,
    name: Optional[str] = None,
    details: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    Update fields on an existing project (patch — only provided fields are changed).

    Args:
        project_id: The numeric project ID (required).
        name:       New project name.
        details:    New project description.
        status:     New project status — "open" or "closed".
    """
    params: dict = {}
    if name is not None:
        params["name"] = name
    if details is not None:
        params["details"] = details
    if status is not None:
        params["status"] = status

    result = await rpc(
        "leantime.rpc.Projects.Projects.patch",
        {"id": project_id, "params": params},
    )
    return "Project updated successfully." if result else "Failed to update project."


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_tickets(
    project_id: Optional[int] = None,
    sprint_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    term: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    List tasks/tickets with optional filters.

    Use this to find tasks by project, sprint, user, status, priority, or free-text search.

    Args:
        project_id: Filter by project ID.
        sprint_id:  Filter by sprint ID. Pass 0 for backlog.
        user_id:    Filter by assigned user ID.
        status:     Filter by status key (e.g. "not_done", "done", or a numeric status ID).
        type:       Filter by ticket type: "task", "subtask", "bug", "story", etc.
        priority:   Filter by priority: "urgent", "high", "medium", "low".
        term:       Free-text search term.
        limit:      Maximum number of tickets to return.
    """
    search_criteria = {
        "currentProject": project_id if project_id is not None else "",
        "sprint": sprint_id if sprint_id is not None else "",
        "users": user_id if user_id is not None else "",
        "status": status if status is not None else "",
        "type": type if type is not None else "",
        "priority": priority if priority is not None else "",
        "term": term if term is not None else "",
        "excludeType": "",
    }
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getAll",
        {"searchCriteria": search_criteria, "limit": limit},
    )
    if not result:
        return "No tickets found."
    return _fmt(result)


@mcp.tool()
async def get_ticket(ticket_id: int) -> str:
    """
    Get full details of a specific task/ticket by its ID.

    Args:
        ticket_id: The numeric ticket ID.
    """
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getTicket",
        {"id": ticket_id},
    )
    if not result:
        return f"Ticket {ticket_id} not found."
    return _fmt(result)


@mcp.tool()
async def create_ticket(
    headline: str,
    project_id: Optional[int] = None,
    description: str = "",
    type: str = "task",
    status: int = 3,
    priority: str = "",
    assigned_to: Optional[int] = None,
    due_date: str = "",
    sprint_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    story_points: Optional[int] = None,
    tags: str = "",
) -> str:
    """
    Create a new task/ticket in a project.

    Args:
        headline:     Task title (required).
        project_id:   Project ID the task belongs to.
        description:  Detailed description of the task.
        type:         Task type: "task" (default), "subtask", "bug", "story", "improvement".
        status:       Status ID (use list_status_labels to see options). Defaults to 3 (New).
        priority:     Task priority — "urgent", "high", "medium", "low".
        assigned_to:  User ID to assign the task to.
        due_date:     Due date in YYYY-MM-DD format.
        sprint_id:    Sprint ID to add this task to.
        milestone_id: Milestone ID to associate with.
        story_points: Story point estimate.
        tags:         Comma-separated tags.
    """
    values = {
        "headline": headline,
        "projectId": project_id if project_id is not None else "",
        "description": description,
        "type": type,
        "status": status,
        "priority": priority,
        "assignedTo": assigned_to if assigned_to is not None else "",
        "dateToFinish": due_date,
        "sprint": sprint_id if sprint_id is not None else "",
        "milestoneid": milestone_id if milestone_id is not None else "",
        "storypoints": story_points if story_points is not None else "",
        "tags": tags,
    }
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.addTicket",
        {"values": values},
    )
    if not result or (isinstance(result, dict) and result.get("status") == "error"):
        msg = result.get("message", "unknown error") if isinstance(result, dict) else "unknown error"
        return f"Failed to create ticket: {msg}"
    ticket_id = result[0] if isinstance(result, list) else result
    return f"Ticket created successfully with ID: {ticket_id}"


@mcp.tool()
async def update_ticket(
    ticket_id: int,
    headline: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[int] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[str] = None,
    sprint_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    story_points: Optional[int] = None,
    tags: Optional[str] = None,
) -> str:
    """
    Update fields on an existing task/ticket (patch — only provided fields are changed).

    Args:
        ticket_id:    The numeric ticket ID (required).
        headline:     New task title.
        description:  New description.
        status:       New status ID.
        priority:     New priority — "urgent", "high", "medium", "low".
        assigned_to:  New assigned user ID.
        due_date:     New due date in YYYY-MM-DD format.
        sprint_id:    Move task to this sprint ID.
        milestone_id: New milestone ID.
        story_points: Updated story point estimate.
        tags:         Updated comma-separated tags.
    """
    params: dict = {}
    if headline is not None:
        params["headline"] = headline
    if description is not None:
        params["description"] = description
    if status is not None:
        params["status"] = status
    if priority is not None:
        params["priority"] = priority
    if assigned_to is not None:
        params["assignedTo"] = assigned_to
    if due_date is not None:
        params["dateToFinish"] = due_date
    if sprint_id is not None:
        params["sprint"] = sprint_id
    if milestone_id is not None:
        params["milestoneid"] = milestone_id
    if story_points is not None:
        params["storypoints"] = story_points
    if tags is not None:
        params["tags"] = tags

    result = await rpc(
        "leantime.rpc.Tickets.Tickets.patch",
        {"id": ticket_id, "params": params},
    )
    return "Ticket updated successfully." if result else "Failed to update ticket."


@mcp.tool()
async def delete_ticket(ticket_id: int) -> str:
    """
    Delete a task/ticket by its ID.

    Args:
        ticket_id: The numeric ticket ID to delete.
    """
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.delete",
        {"id": ticket_id},
    )
    if isinstance(result, dict) and result.get("status") == "error":
        return f"Failed to delete ticket: {result.get('message', 'unknown error')}"
    return f"Ticket {ticket_id} deleted successfully."


@mcp.tool()
async def search_tickets(
    term: str,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> str:
    """
    Search for tasks/tickets by keyword across all projects.

    Args:
        term:       Search term (required).
        project_id: Limit search to a specific project.
        user_id:    Limit search to a specific user.
    """
    search_criteria = {
        "currentProject": project_id if project_id is not None else "",
        "users": user_id if user_id is not None else "",
        "term": term,
        "status": "",
        "sprint": "",
        "excludeType": "",
    }
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getAll",
        {"searchCriteria": search_criteria},
    )
    if not result:
        return f'No tickets found matching "{term}".'
    return _fmt(result)


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_milestones(
    project_id: int,
    include_archived: bool = False,
) -> str:
    """
    List milestones for a project.

    Args:
        project_id:       Project ID to list milestones for (required).
        include_archived: Include archived milestones. Defaults to False.
    """
    search_criteria = {
        "currentProject": project_id,
        "type": "milestone",
    }
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getAllMilestones",
        {"searchCriteria": search_criteria},
    )
    if not result:
        return "No milestones found."
    return _fmt(result)


@mcp.tool()
async def create_milestone(
    headline: str,
    project_id: int,
    due_date: str = "",
    description: str = "",
) -> str:
    """
    Create a new milestone in a project.

    Args:
        headline:    Milestone title (required).
        project_id:  Project ID (required).
        due_date:    Target completion date in YYYY-MM-DD format.
        description: Milestone description.
    """
    params = {
        "headline": headline,
        "projectId": project_id,
        "description": description,
        "dateToFinish": due_date,
        "type": "milestone",
    }
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.quickAddMilestone",
        {"params": params},
    )
    if not result or (isinstance(result, dict) and result.get("status") == "error"):
        msg = result.get("message", "unknown error") if isinstance(result, dict) else "unknown error"
        return f"Failed to create milestone: {msg}"
    milestone_id = result[0] if isinstance(result, list) else result
    return f"Milestone created successfully with ID: {milestone_id}"


# ---------------------------------------------------------------------------
# Sprints
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_sprints(project_id: int) -> str:
    """
    List all sprints for a project.

    Args:
        project_id: Project ID to list sprints for (required).
    """
    result = await rpc(
        "leantime.rpc.Sprints.Sprints.getAllSprints",
        {"projectId": project_id},
    )
    if not result:
        return "No sprints found."
    return _fmt(result)


@mcp.tool()
async def get_current_sprint(project_id: int) -> str:
    """
    Get the ID of the currently active sprint for a project.

    Args:
        project_id: Project ID (required).
    """
    result = await rpc(
        "leantime.rpc.Sprints.Sprints.getCurrentSprintId",
        {"projectId": project_id},
    )
    if not result:
        return f"No active sprint found for project {project_id}."
    return f"Current sprint ID: {result}"


@mcp.tool()
async def create_sprint(
    name: str,
    project_id: int,
    start_date: str = "",
    end_date: str = "",
) -> str:
    """
    Create a new sprint for a project.

    Args:
        name:       Sprint name (required).
        project_id: Project ID (required).
        start_date: Sprint start date in YYYY-MM-DD format.
        end_date:   Sprint end date in YYYY-MM-DD format.
    """
    params = {
        "name": name,
        "projectId": project_id,
        "startDate": start_date,
        "endDate": end_date,
    }
    result = await rpc(
        "leantime.rpc.Sprints.Sprints.addSprint",
        {"params": params},
    )
    if not result:
        return "Failed to create sprint."
    return f"Sprint created successfully with ID: {result}"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_users(active_only: bool = True) -> str:
    """
    List all users in the system.

    Args:
        active_only: Return only active users. Defaults to True.
    """
    result = await rpc(
        "leantime.rpc.Users.Users.getAll",
        {"activeOnly": active_only},
    )
    if not result:
        return "No users found."
    # Return a lightweight summary to avoid flooding context.
    if isinstance(result, list):
        summary = [
            {
                "id": u.get("id"),
                "name": (
                    f"{u.get('firstname', '')} {u.get('lastname', '')}".strip()
                    or u.get("username")
                ),
                "email": u.get("username"),
                "role": u.get("role"),
                "status": u.get("status"),
            }
            for u in result
        ]
    else:
        summary = result
    return _fmt(summary)


@mcp.tool()
async def get_user(user_id: int) -> str:
    """
    Get details of a specific user by ID.

    Args:
        user_id: The numeric user ID (required).
    """
    result = await rpc(
        "leantime.rpc.Users.Users.getUser",
        {"id": user_id},
    )
    if not result:
        return f"User {user_id} not found."
    return _fmt(result)


@mcp.tool()
async def list_project_users(project_id: int) -> str:
    """
    List all users assigned to a specific project.

    Args:
        project_id: The project ID (required).
    """
    result = await rpc(
        "leantime.rpc.Projects.Projects.getUsersAssignedToProject",
        {"projectId": project_id},
    )
    if not result:
        return f"No users found for project {project_id}."
    return _fmt(result)


# ---------------------------------------------------------------------------
# Timesheets
# ---------------------------------------------------------------------------


@mcp.tool()
async def log_time(
    ticket_id: int,
    hours: float,
    work_date: Optional[str] = None,
    description: str = "",
    kind: str = "general",
) -> str:
    """
    Log time worked on a ticket.

    Args:
        ticket_id:   The ticket/task ID to log time against (required).
        hours:       Number of hours to log, e.g. 1.5 for 90 minutes (required).
        work_date:   Date the work was done in YYYY-MM-DD format. Defaults to today.
        description: Description of work done.
        kind:        Type of work: "general" (default), "dev", "design", "management", "testing".
    """
    work_date = work_date if work_date else _today()
    params = {
        "hours": hours,
        "date": work_date,
        "description": description,
        "kind": kind,
    }
    result = await rpc(
        "leantime.rpc.Timesheets.Timesheets.logTime",
        {"ticketId": ticket_id, "params": params},
    )
    if not result or (isinstance(result, dict) and result.get("status") == "error"):
        msg = result.get("message", "unknown error") if isinstance(result, dict) else "unknown error"
        return f"Failed to log time: {msg}"
    return f"Logged {hours} hours on ticket {ticket_id} for {work_date}."


def _today() -> str:
    """Return today's date as a YYYY-MM-DD string."""
    return date.today().isoformat()


@mcp.tool()
async def get_timesheets(
    date_from: str,
    date_to: str,
    project_id: int = -1,
    user_id: Optional[int] = None,
) -> str:
    """
    Get timesheet entries for a date range and optional project.

    Args:
        date_from:  Start date in YYYY-MM-DD format (required).
        date_to:    End date in YYYY-MM-DD format (required).
        project_id: Filter by project ID. Pass -1 for all projects (default).
        user_id:    Filter by user ID.
    """
    result = await rpc(
        "leantime.rpc.Timesheets.Timesheets.getAll",
        {
            "dateFrom": date_from,
            "dateTo": date_to,
            "projectId": project_id,
            "userId": user_id,
            "kind": "all",
        },
    )
    if not result:
        return "No timesheet entries found."
    return _fmt(result)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


@mcp.tool()
async def add_comment(ticket_id: int, comment: str) -> str:
    """
    Add a comment to a ticket/task.

    Args:
        ticket_id: The ticket ID to comment on (required).
        comment:   The comment text (required).
    """
    values = {
        "text": comment,
        "moduleId": ticket_id,
        "commentParent": 0,
    }
    result = await rpc(
        "leantime.rpc.Comments.Comments.addComment",
        {
            "values": values,
            "module": "tickets",
            "entityId": ticket_id,
            "entity": {},
        },
    )
    return "Comment added successfully." if result else "Failed to add comment."


@mcp.tool()
async def list_comments(ticket_id: int) -> str:
    """
    List all comments on a ticket/task.

    Args:
        ticket_id: The ticket ID to get comments for (required).
    """
    result = await rpc(
        "leantime.rpc.Comments.Comments.getComments",
        {
            "module": "tickets",
            "entityId": ticket_id,
        },
    )
    if not result:
        return f"No comments found on ticket {ticket_id}."
    return _fmt(result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_status_labels(project_id: Optional[int] = None) -> str:
    """
    List available status labels for a project.

    Use this to find the correct status IDs when creating or updating tickets.

    Args:
        project_id: Project ID to get statuses for.
                    If omitted, returns statuses for the current project.
    """
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getStatusLabels",
        {"projectId": project_id},
    )
    if not result:
        return "No status labels found."
    return _fmt(result)


@mcp.tool()
async def list_ticket_types() -> str:
    """List all available ticket/task types (task, bug, story, etc.)."""
    result = await rpc(
        "leantime.rpc.Tickets.Tickets.getTicketTypes",
        {},
    )
    return _fmt(result)


@mcp.tool()
async def get_project_progress(project_id: int) -> str:
    """
    Get the completion progress of a project as a percentage with estimated completion date.

    Args:
        project_id: Project ID (required).
    """
    result = await rpc(
        "leantime.rpc.Projects.Projects.getProjectProgress",
        {"projectId": project_id},
    )
    if not result:
        return "Could not get project progress."
    return _fmt(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
