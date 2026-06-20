"""
Section 18 — TaskComment: seed data + unauthenticated GET operations.

Creates taskComments that subsequent sections depend on.

Populates ctx.state: taskComment1_id, taskComment2_id, taskComment3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
  task1_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("18 · TASKCOMMENT — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    task1_id = ctx.state.get("task1_id")

    # --- Seed: create taskComments ---

    _create_path = f"/api/tasks/{task1_id}/comments"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "body": 'Test content 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create taskComment1"):
        data = ctx.safe_json(resp)
        ctx.state["taskComment1_id"] = data.get("id")
        if data.get("authorId") == user1_id:
            ctx.ok("authorId injected from JWT")
        else:
            ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")
        if data.get("taskId") == task1_id:
            ctx.ok("taskId injected from URL param")
        else:
            ctx.fail(f"taskId mismatch: expected {task1_id}, got {data.get('taskId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "body": 'Test content 2',
    })
    if ctx.assert_status(resp, 201, "Seed: Create taskComment2"):
        data = ctx.safe_json(resp)
        ctx.state["taskComment2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "body": 'Test content 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create taskComment3"):
        data = ctx.safe_json(resp)
        ctx.state["taskComment3_id"] = data.get("id")

    # --- GET tests ---

    # 18-1  Paginated list
    resp = ctx.req("GET", "/api/taskComments")
    if ctx.assert_status(resp, 200, "GET /api/taskComments → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/taskComments")

    # 18-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/taskComments", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/taskComments?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 18-3  GET by ID
    taskComment1_id = ctx.state.get("taskComment1_id")
    if taskComment1_id:
        resp = ctx.req("GET", "/api/taskComments/" + str(taskComment1_id))
        if ctx.assert_status(resp, 200, f"GET /api/taskComments/{taskComment1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == taskComment1_id:
                ctx.ok("TaskComment id matches requested id")
            else:
                ctx.fail(f"TaskComment id mismatch: {data.get('id')} vs {taskComment1_id}")
    else:
        ctx.skip("GET /api/taskComments/:id — seed ID not available (seed may have failed)")

    # 18-4  Non-existent → 404
    resp = ctx.req("GET", "/api/taskComments/9999999")
    ctx.assert_status(resp, 404, "GET /api/taskComments/9999999 → 404")

    # 18-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/taskComments/notanid")
    ctx.assert_status(resp, 400, "GET /api/taskComments/notanid → 400 (invalid ID)")

    # 18-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/taskComments/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/taskComments/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/taskComments/-5 → unexpected HTTP {resp.status_code}")
