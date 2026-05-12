import asyncio
import json
import os

import httpx

BASE_URL = os.environ.get("LEANTIME_BASE_URL", "http://192.168.2.48:8080").strip()
API_KEY  = os.environ.get("LEANTIME_API_KEY", "lt_scXGZxob1bCyw99zwypjJ4vx5F94ehSJ_mcYS8SuAC641d9lwiVaJZm3UklMPeGFzcd").strip()

print(f"BASE_URL : {BASE_URL}")
print(f"API_KEY  : {API_KEY[:12]}...")


async def raw_test():
    """Bare httpx call — same as curl, no server.py involved."""
    payload = {
        "jsonrpc": "2.0",
        "method": "leantime.rpc.Projects.Projects.getAll",
        "params": {"showClosedProjects": False},
        "id": 1,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BASE_URL}/api/jsonrpc",
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
            },
            content=json.dumps(payload),
        )
    print(f"HTTP {r.status_code}")
    print(r.text[:500])


# Set env vars before importing server
os.environ["LEANTIME_BASE_URL"] = BASE_URL
os.environ["LEANTIME_API_KEY"]  = API_KEY

from server import (
    list_projects,
    get_project,
    list_tickets,
    get_ticket,
    list_users,
    list_status_labels,
    list_ticket_types,
)


async def main():
    print("\n=== raw httpx (no MCP) ===")
    await raw_test()

    print("\n=== list_projects (via server.py) ===")
    result = await list_projects(status="open")
    print(result[:500])

    # Uncomment to test more tools:

    # print("\n=== list_users ===")
    # print(await list_users())

    # print("\n=== list_status_labels ===")
    # print(await list_status_labels())

    # print("\n=== list_ticket_types ===")
    # print(await list_ticket_types())

    # print("\n=== list_tickets ===")
    # print(await list_tickets())

    # print("\n=== get_project ===")
    # print(await get_project(project_id=1))

    # print("\n=== get_ticket ===")
    # print(await get_ticket(ticket_id=1))


if __name__ == "__main__":
    asyncio.run(main())
