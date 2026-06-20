"""
Section 14 — Project: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  project1_id, project2_id, project3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("14 · PROJECT — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    project1_id = ctx.state.get("project1_id")
    project2_id = ctx.state.get("project2_id")
    project3_id = ctx.state.get("project3_id")
    organization1_id = ctx.state.get("organization1_id")
    _create_path = f"/api/organizations/{organization1_id}/projects"

    # 14-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "name": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/organizations/:id/projects without auth → 401",
                      auth_fail=True)

    # 14-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/organizations/:id/projects empty body → 400")

# LLM_SECTION_START
# Generate required-field validation tests for entity "Project".
# Canonical create path: /api/organizations/:id/projects
# Requires authentication: True
#
# Required scalar fields (excluding server-injected FK fields):
#   name: string (required)
#
# If the required fields list above is EMPTY, output only this single comment line and nothing else:
#   # (no required fields to validate)
#
# Otherwise, for EACH required field, generate one test:
#   - Omit only that field from the body
#   - Include all other required fields with sensible values
#   - MUST also include every secondary FK listed below in the body (they are required by the API)
#   - Expect HTTP 400: ctx.assert_status(resp, 400, "POST project missing <field> → 400")
#   - Wrap in `if token1:` guard
#
# Then generate ONE ownership spoofing test for the owner FK (if present):
#
# Available variables (already declared above):
#   token1, token2
#   user1_id, user2_id
#   project1_id, project2_id, project3_id
# LLM_SECTION_END    # 14-update  PUT happy path → 200
    if project1_id and token1:
        _update_val: str | int = "Updated Project"
        resp = ctx.req("PUT", "/api/projects/" + str(project1_id),
                       token=token1,
                       body={"name": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/projects/{project1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("name") == _update_val:
                ctx.ok("Updated 'name' returned correctly")
            else:
                ctx.fail("Updated 'name' mismatch in response")
    else:
        ctx.skip("PUT /api/projects/:id by owner — seed ID or token not available")

    # 14-auth  PUT without auth → 401
    if project1_id:
        resp = ctx.req("PUT", "/api/projects/" + str(project1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/projects/{project1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/projects/:id without auth — seed ID not available")


    # 14-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/projects/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/projects/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/projects/9999999 — token not available")

    # 14-delete-noauth  DELETE without auth → 401
    if project2_id:
        resp = ctx.req("DELETE", "/api/projects/" + str(project2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/projects/{project2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/projects/:id without auth — seed ID2 not available")


    # 14-delete-owner  DELETE by owner → 204
    if project2_id and token1:
        resp = ctx.req("DELETE", "/api/projects/" + str(project2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/projects/{project2_id} by owner → 204"):
            ctx.state["project2_deleted"] = True
    else:
        ctx.skip("DELETE /api/projects/:id by owner — seed ID2 or token not available")

    # 14-get-deleted  GET after delete → 404
    if project2_id and ctx.state.get("project2_deleted"):
        resp = ctx.req("GET", "/api/projects/" + str(project2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/projects/{project2_id} after deletion → 404")

    # 14-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/projects/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/projects/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/projects/9999999 — token not available")
