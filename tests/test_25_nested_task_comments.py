"""
Section 25 — Nested routes: GET/POST /api/tasks/:id/comments.

Task is the primary parent of TaskComment. The taskId
is injected from the URL param. The authorId (if present) is injected from JWT.

Populates ctx.state: parent_nested_taskComment_id.
Requires ctx.state:
  user1_id, user1_token, user2_id, user2_token
  task1_id, task3_id (from tasks seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("25 · NESTED ROUTES — /api/tasks/:id/comments")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    task1_id = ctx.state.get("task1_id")
    task3_id = ctx.state.get("task3_id")

    # 25-1  GET → 200 paginated, scoped to parent
    if task1_id:
        resp = ctx.req("GET",
                       "/api/tasks/" + str(task1_id) + "/comments")
        if ctx.assert_status(resp, 200,
                             f"GET /api/tasks/{task1_id}/comments → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/tasks/{task1_id}/comments")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("taskId") != task1_id]
            if wrong:
                ctx.fail(f"taskComments list contains items for other parents: {wrong}")
            else:
                ctx.ok(f"All comments correctly scoped to task1")

    # 25-2  GET pagination
    if task1_id:
        resp = ctx.req("GET",
                       "/api/tasks/" + str(task1_id) + "/comments",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/tasks/{task1_id}/comments?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on parent-nested comments")

    # 25-3  Non-existent parent → empty list (not 404)
    resp = ctx.req("GET", "/api/tasks/9999999/comments")
    if ctx.assert_status(resp, 200,
                         "GET /api/tasks/9999999/comments → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent parent's comments returns total=0")

    # 25-4  POST without auth → 401
    if task1_id:
        resp = ctx.req("POST",
                       "/api/tasks/" + str(task1_id) + "/comments",
                       body={
                           "body": "Anonymous attempt",
                       })
        ctx.assert_status(resp, 401,
                          f"POST /api/tasks/{task1_id}/comments without auth → 401",
                          auth_fail=True)

    # 25-5  POST with auth, missing required fields → 400
    if task1_id and token1:
        resp = ctx.req("POST",
                       "/api/tasks/" + str(task1_id) + "/comments",
                       token=token1,
                       body={
                       })
        ctx.assert_status(resp, 400,
                          f"POST nested comments missing body → 400")

    # 25-6  POST with auth — taskId injected from URL
    parent_nested_child_id = None
    if task1_id and token1:
        resp = ctx.req("POST",
                       "/api/tasks/" + str(task1_id) + "/comments",
                       token=token1,
                       body={
                           "body": 'Test content 1',
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested TaskComment (parent-scoped)"):
            data = ctx.safe_json(resp)
            parent_nested_child_id = data.get("id")
            ctx.state["parent_nested_taskComment_id"] = parent_nested_child_id
            if data.get("taskId") == task1_id:
                ctx.ok("taskId injected correctly from URL param")
            else:
                ctx.fail(f"taskId mismatch: expected {task1_id}, got {data.get('taskId')}")
            if data.get("authorId") == user1_id:
                ctx.ok("authorId injected correctly from JWT")
            else:
                ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")

    # 25-7  Security: owner FK spoofing via nested route
    if task1_id and token1 and user2_id:
        resp = ctx.req("POST",
                       "/api/tasks/" + str(task1_id) + "/comments",
                       token=token1,
                       body={
                           "body": "Claimed by user2",
                           "authorId": "SPOOFED_VALUE",
                       })
        if resp.status_code == 201:
            data = ctx.safe_json(resp)
            spoofed_id = ctx.state.get("parent_nested_taskComment_id")
            if data.get("authorId") == user2_id:
                ctx.warn(
                    f"SECURITY: POST /api/tasks/:id/comments allows arbitrary authorId — "
                    "should inject from JWT instead."
                )
                ctx.state["spoofed_taskComment_id"] = data.get("id")
            elif data.get("authorId") == user1_id:
                ctx.ok("POST nested: authorId spoof ignored, set from token")
