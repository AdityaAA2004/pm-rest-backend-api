"""
Section 15 — Task: seed data + unauthenticated GET operations.

Creates tasks that subsequent sections depend on.

Populates ctx.state: task1_id, task2_id, task3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
  project1_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("15 · TASK — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    project1_id = ctx.state.get("project1_id")

    # --- Seed: create tasks ---

    _create_path = f"/api/projects/{project1_id}/tasks"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create task1"):
        data = ctx.safe_json(resp)
        ctx.state["task1_id"] = data.get("id")
        if data.get("projectId") == project1_id:
            ctx.ok("projectId injected from URL param")
        else:
            ctx.fail(f"projectId mismatch: expected {project1_id}, got {data.get('projectId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 2',
        "description": 'Test description 2',
        "status": 'todo',
        "priority": 2,
    })
    if ctx.assert_status(resp, 201, "Seed: Create task2"):
        data = ctx.safe_json(resp)
        ctx.state["task2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "title": 'Test Title 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create task3"):
        data = ctx.safe_json(resp)
        ctx.state["task3_id"] = data.get("id")

    # --- GET tests ---

    # 15-1  Paginated list
    resp = ctx.req("GET", "/api/tasks")
    if ctx.assert_status(resp, 200, "GET /api/tasks → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/tasks")

    # 15-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/tasks", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/tasks?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 15-3  GET by ID
    task1_id = ctx.state.get("task1_id")
    if task1_id:
        resp = ctx.req("GET", "/api/tasks/" + str(task1_id))
        if ctx.assert_status(resp, 200, f"GET /api/tasks/{task1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == task1_id:
                ctx.ok("Task id matches requested id")
            else:
                ctx.fail(f"Task id mismatch: {data.get('id')} vs {task1_id}")
    else:
        ctx.skip("GET /api/tasks/:id — seed ID not available (seed may have failed)")

    # 15-4  Non-existent → 404
    resp = ctx.req("GET", "/api/tasks/9999999")
    ctx.assert_status(resp, 404, "GET /api/tasks/9999999 → 404")

    # 15-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/tasks/notanid")
    ctx.assert_status(resp, 400, "GET /api/tasks/notanid → 400 (invalid ID)")

    # 15-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/tasks/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/tasks/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/tasks/-5 → unexpected HTTP {resp.status_code}")
