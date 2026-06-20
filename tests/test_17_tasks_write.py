"""
Section 17 — Task: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  task1_id, task2_id, task3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("17 · TASK — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    task1_id = ctx.state.get("task1_id")
    task2_id = ctx.state.get("task2_id")
    task3_id = ctx.state.get("task3_id")
    project1_id = ctx.state.get("project1_id")
    _create_path = f"/api/projects/{project1_id}/tasks"

    # 17-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "title": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/projects/:id/tasks without auth → 401",
                      auth_fail=True)

    # 17-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/projects/:id/tasks empty body → 400")

# LLM_SECTION_START
# Generate required-field validation tests for entity "Task".
# Canonical create path: /api/projects/:id/tasks
# Requires authentication: True
#
# Required scalar fields (excluding server-injected FK fields):
#   title: string (required)
#
# If the required fields list above is EMPTY, output only this single comment line and nothing else:
#   # (no required fields to validate)
#
# Otherwise, for EACH required field, generate one test:
#   - Omit only that field from the body
#   - Include all other required fields with sensible values
#   - MUST also include every secondary FK listed below in the body (they are required by the API)
#   - Expect HTTP 400: ctx.assert_status(resp, 400, "POST task missing <field> → 400")
#   - Wrap in `if token1:` guard
#
# Then generate ONE ownership spoofing test for the owner FK (if present):
#
# Available variables (already declared above):
#   token1, token2
#   user1_id, user2_id
#   task1_id, task2_id, task3_id
# LLM_SECTION_END    # 17-update  PUT happy path → 200
    if task1_id and token1:
        _update_val: str | int = "Updated Task"
        resp = ctx.req("PUT", "/api/tasks/" + str(task1_id),
                       token=token1,
                       body={"title": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/tasks/{task1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("title") == _update_val:
                ctx.ok("Updated 'title' returned correctly")
            else:
                ctx.fail("Updated 'title' mismatch in response")
    else:
        ctx.skip("PUT /api/tasks/:id by owner — seed ID or token not available")

    # 17-auth  PUT without auth → 401
    if task1_id:
        resp = ctx.req("PUT", "/api/tasks/" + str(task1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/tasks/{task1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/tasks/:id without auth — seed ID not available")


    # 17-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/tasks/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/tasks/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/tasks/9999999 — token not available")

    # 17-delete-noauth  DELETE without auth → 401
    if task2_id:
        resp = ctx.req("DELETE", "/api/tasks/" + str(task2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/tasks/{task2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/tasks/:id without auth — seed ID2 not available")


    # 17-delete-owner  DELETE by owner → 204
    if task2_id and token1:
        resp = ctx.req("DELETE", "/api/tasks/" + str(task2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/tasks/{task2_id} by owner → 204"):
            ctx.state["task2_deleted"] = True
    else:
        ctx.skip("DELETE /api/tasks/:id by owner — seed ID2 or token not available")

    # 17-get-deleted  GET after delete → 404
    if task2_id and ctx.state.get("task2_deleted"):
        resp = ctx.req("GET", "/api/tasks/" + str(task2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/tasks/{task2_id} after deletion → 404")

    # 17-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/tasks/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/tasks/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/tasks/9999999 — token not available")
