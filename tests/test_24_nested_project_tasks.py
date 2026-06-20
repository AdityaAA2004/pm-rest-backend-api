"""
Section 24 — Nested routes: GET/POST /api/projects/:id/tasks.

Project is the primary parent of Task. The projectId
is injected from the URL param. The None (if present) is injected from JWT.

Populates ctx.state: parent_nested_task_id.
Requires ctx.state:
  user1_id, user1_token, user2_id, user2_token
  project1_id, project3_id (from projects seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("24 · NESTED ROUTES — /api/projects/:id/tasks")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    project1_id = ctx.state.get("project1_id")
    project3_id = ctx.state.get("project3_id")

    # 24-1  GET → 200 paginated, scoped to parent
    if project1_id:
        resp = ctx.req("GET",
                       "/api/projects/" + str(project1_id) + "/tasks")
        if ctx.assert_status(resp, 200,
                             f"GET /api/projects/{project1_id}/tasks → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/projects/{project1_id}/tasks")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("projectId") != project1_id]
            if wrong:
                ctx.fail(f"tasks list contains items for other parents: {wrong}")
            else:
                ctx.ok(f"All tasks correctly scoped to project1")

    # 24-2  GET pagination
    if project1_id:
        resp = ctx.req("GET",
                       "/api/projects/" + str(project1_id) + "/tasks",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/projects/{project1_id}/tasks?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on parent-nested tasks")

    # 24-3  Non-existent parent → empty list (not 404)
    resp = ctx.req("GET", "/api/projects/9999999/tasks")
    if ctx.assert_status(resp, 200,
                         "GET /api/projects/9999999/tasks → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent parent's tasks returns total=0")

    # 24-4  POST without auth → 401
    if project1_id:
        resp = ctx.req("POST",
                       "/api/projects/" + str(project1_id) + "/tasks",
                       body={
                           "title": "Anonymous attempt",
                       })
        ctx.assert_status(resp, 401,
                          f"POST /api/projects/{project1_id}/tasks without auth → 401",
                          auth_fail=True)

    # 24-5  POST with auth, missing required fields → 400
    if project1_id and token1:
        resp = ctx.req("POST",
                       "/api/projects/" + str(project1_id) + "/tasks",
                       token=token1,
                       body={
                       })
        ctx.assert_status(resp, 400,
                          f"POST nested tasks missing title → 400")

    # 24-6  POST with auth — projectId injected from URL
    parent_nested_child_id = None
    if project1_id and token1:
        resp = ctx.req("POST",
                       "/api/projects/" + str(project1_id) + "/tasks",
                       token=token1,
                       body={
                           "title": 'Test Title 1',
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested Task (parent-scoped)"):
            data = ctx.safe_json(resp)
            parent_nested_child_id = data.get("id")
            ctx.state["parent_nested_task_id"] = parent_nested_child_id
            if data.get("projectId") == project1_id:
                ctx.ok("projectId injected correctly from URL param")
            else:
                ctx.fail(f"projectId mismatch: expected {project1_id}, got {data.get('projectId')}")

