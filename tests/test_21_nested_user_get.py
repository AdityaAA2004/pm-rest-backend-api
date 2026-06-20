"""
Section 21 — Nested routes: GET /api/users/:id/<child_plural>.

Tests all nested GET routes under User — each returns a paginated,
FK-scoped list of child resources.

Requires ctx.state: user1_id
  and membership1_id (from memberships seed section)
  and task1_id (from tasks seed section)
  and taskComment1_id (from taskComments seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("21 · NESTED ROUTES — GET /api/users/:id/<child>")

    user1_id = ctx.state.get("user1_id")

    # ── GET /api/users/:id/memberships ──────────────────────────────────

    # 21-1  Paginated, scoped to user
    if user1_id:
        resp = ctx.req("GET", "/api/users/" + str(user1_id) + "/memberships")
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/memberships → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/users/{user1_id}/memberships")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("userId") != user1_id]
            if wrong:
                ctx.fail(
                    f"GET /api/users/{user1_id}/memberships "
                    f"returned items with wrong userId: {[i.get('userId') for i in wrong]}"
                )
            else:
                ctx.ok(f"All memberships correctly scoped to user1")

    # 21-2  Pagination limit=1 on nested memberships
    if user1_id:
        resp = ctx.req("GET",
                       "/api/users/" + str(user1_id) + "/memberships",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/memberships?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on nested user/memberships")
            else:
                ctx.fail(f"Expected limit=1, got {meta.get('limit')}")

    # ── GET /api/users/:id/tasks ──────────────────────────────────

    # 21-3  Paginated, scoped to user
    if user1_id:
        resp = ctx.req("GET", "/api/users/" + str(user1_id) + "/tasks")
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/tasks → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/users/{user1_id}/tasks")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("assigneeId") != user1_id]
            if wrong:
                ctx.fail(
                    f"GET /api/users/{user1_id}/tasks "
                    f"returned items with wrong assigneeId: {[i.get('assigneeId') for i in wrong]}"
                )
            else:
                ctx.ok(f"All tasks correctly scoped to user1")

    # 21-4  Pagination limit=1 on nested tasks
    if user1_id:
        resp = ctx.req("GET",
                       "/api/users/" + str(user1_id) + "/tasks",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/tasks?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on nested user/tasks")
            else:
                ctx.fail(f"Expected limit=1, got {meta.get('limit')}")

    # ── GET /api/users/:id/comments ──────────────────────────────────

    # 21-5  Paginated, scoped to user
    if user1_id:
        resp = ctx.req("GET", "/api/users/" + str(user1_id) + "/comments")
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/comments → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/users/{user1_id}/comments")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("authorId") != user1_id]
            if wrong:
                ctx.fail(
                    f"GET /api/users/{user1_id}/comments "
                    f"returned items with wrong authorId: {[i.get('authorId') for i in wrong]}"
                )
            else:
                ctx.ok(f"All comments correctly scoped to user1")

    # 21-6  Pagination limit=1 on nested comments
    if user1_id:
        resp = ctx.req("GET",
                       "/api/users/" + str(user1_id) + "/comments",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/users/{user1_id}/comments?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on nested user/comments")
            else:
                ctx.fail(f"Expected limit=1, got {meta.get('limit')}")


    # Non-existent user → empty paginated list (not 404)
    resp = ctx.req("GET", "/api/users/9999999/memberships")
    if ctx.assert_status(resp, 200,
                         "GET /api/users/9999999/memberships → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent user's memberships returns total=0")
        else:
            ctx.fail(f"Expected total=0 for non-existent user, got {total}")

    resp = ctx.req("GET", "/api/users/9999999/tasks")
    if ctx.assert_status(resp, 200,
                         "GET /api/users/9999999/tasks → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent user's tasks returns total=0")
        else:
            ctx.fail(f"Expected total=0 for non-existent user, got {total}")

    resp = ctx.req("GET", "/api/users/9999999/comments")
    if ctx.assert_status(resp, 200,
                         "GET /api/users/9999999/comments → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent user's comments returns total=0")
        else:
            ctx.fail(f"Expected total=0 for non-existent user, got {total}")


    # Invalid user ID format → 400
    resp = ctx.req("GET", "/api/users/abc/memberships")
    ctx.assert_status(resp, 400,
                      "GET /api/users/abc/memberships → 400 (invalid ID)")
    resp = ctx.req("GET", "/api/users/abc/tasks")
    ctx.assert_status(resp, 400,
                      "GET /api/users/abc/tasks → 400 (invalid ID)")
    resp = ctx.req("GET", "/api/users/abc/comments")
    ctx.assert_status(resp, 400,
                      "GET /api/users/abc/comments → 400 (invalid ID)")
