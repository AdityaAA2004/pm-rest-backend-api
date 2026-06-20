"""
Section 20 — TaskComment: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  taskComment1_id, taskComment2_id, taskComment3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("20 · TASKCOMMENT — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    taskComment1_id = ctx.state.get("taskComment1_id")
    taskComment2_id = ctx.state.get("taskComment2_id")
    taskComment3_id = ctx.state.get("taskComment3_id")
    task1_id = ctx.state.get("task1_id")
    _create_path = f"/api/tasks/{task1_id}/comments"

    # 20-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "body": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/tasks/:id/comments without auth → 401",
                      auth_fail=True)

    # 20-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/tasks/:id/comments empty body → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={})  # body omitted
        ctx.assert_status(resp, 400, "POST taskComment missing body → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"body": "Test comment", "authorId": user2_id})
        data = ctx.safe_json(resp)
        if resp.status_code == 201 and data.get("authorId") == user1_id:
            ctx.ok("ownership spoofing prevented — authorId correctly overridden")
        elif resp.status_code == 201 and data.get("authorId") == user2_id:
            ctx.warn("SECURITY: ownership spoofing succeeded — authorId accepted from body")
        if resp.status_code == 201:
            ctx.state["spoofed_taskComment_id"] = data.get("id")

    # 20-update  PUT happy path → 200
    if taskComment1_id and token1:
        _update_val: str | int = "Updated TaskComment"
        resp = ctx.req("PUT", "/api/taskComments/" + str(taskComment1_id),
                       token=token1,
                       body={"body": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/taskComments/{taskComment1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("body") == _update_val:
                ctx.ok("Updated 'body' returned correctly")
            else:
                ctx.fail("Updated 'body' mismatch in response")
    else:
        ctx.skip("PUT /api/taskComments/:id by owner — seed ID or token not available")

    # 20-auth  PUT without auth → 401
    if taskComment1_id:
        resp = ctx.req("PUT", "/api/taskComments/" + str(taskComment1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/taskComments/{taskComment1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/taskComments/:id without auth — seed ID not available")

    # 20-owner  PUT by non-owner → 403
    if taskComment1_id and token2:
        resp = ctx.req("PUT", "/api/taskComments/" + str(taskComment1_id),
                       token=token2,
                       body={"title": "Hijack attempt"})
        ctx.assert_status(resp, 403,
                          f"PUT /api/taskComments/{taskComment1_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/taskComments/:id by non-owner — seed ID or token2 not available")

    # 20-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/taskComments/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/taskComments/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/taskComments/9999999 — token not available")

    # 20-delete-noauth  DELETE without auth → 401
    if taskComment2_id:
        resp = ctx.req("DELETE", "/api/taskComments/" + str(taskComment2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/taskComments/{taskComment2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/taskComments/:id without auth — seed ID2 not available")

    # 20-delete-nonowner  DELETE by non-owner → 403
    if taskComment2_id and token2:
        resp = ctx.req("DELETE", "/api/taskComments/" + str(taskComment2_id),
                       token=token2)
        ctx.assert_status(resp, 403,
                          f"DELETE /api/taskComments/{taskComment2_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/taskComments/:id by non-owner — seed ID2 or token2 not available")

    # 20-delete-owner  DELETE by owner → 204
    if taskComment2_id and token1:
        resp = ctx.req("DELETE", "/api/taskComments/" + str(taskComment2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/taskComments/{taskComment2_id} by owner → 204"):
            ctx.state["taskComment2_deleted"] = True
    else:
        ctx.skip("DELETE /api/taskComments/:id by owner — seed ID2 or token not available")

    # 20-get-deleted  GET after delete → 404
    if taskComment2_id and ctx.state.get("taskComment2_deleted"):
        resp = ctx.req("GET", "/api/taskComments/" + str(taskComment2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/taskComments/{taskComment2_id} after deletion → 404")

    # 20-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/taskComments/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/taskComments/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/taskComments/9999999 — token not available")
