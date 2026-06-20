"""
Section 8 — Organization: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  organization1_id, organization2_id, organization3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("8 · ORGANIZATION — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    organization1_id = ctx.state.get("organization1_id")
    organization2_id = ctx.state.get("organization2_id")
    organization3_id = ctx.state.get("organization3_id")
    _create_path = "/api/organizations"

    # 8-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "name": "Anon Test",
        "slug": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/organizations without auth → 401",
                      auth_fail=True)

    # 8-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/organizations empty body → 400")

# LLM_SECTION_START
# Generate required-field validation tests for entity "Organization".
# Canonical create path: /api/organizations
# Requires authentication: True
#
# Required scalar fields (excluding server-injected FK fields):
#   name: string (required)
#   slug: string (required)
#
# If the required fields list above is EMPTY, output only this single comment line and nothing else:
#   # (no required fields to validate)
#
# Otherwise, for EACH required field, generate one test:
#   - Omit only that field from the body
#   - Include all other required fields with sensible values
#   - MUST also include every secondary FK listed below in the body (they are required by the API)
#   - Expect HTTP 400: ctx.assert_status(resp, 400, "POST organization missing <field> → 400")
#   - Wrap in `if token1:` guard
#
# Then generate ONE ownership spoofing test for the owner FK (if present):
#
# Available variables (already declared above):
#   token1, token2
#   user1_id, user2_id
#   organization1_id, organization2_id, organization3_id
# LLM_SECTION_END    # 8-update  PUT happy path → 200
    if organization1_id and token1:
        _update_val: str | int = "Updated Organization"
        resp = ctx.req("PUT", "/api/organizations/" + str(organization1_id),
                       token=token1,
                       body={"name": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/organizations/{organization1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("name") == _update_val:
                ctx.ok("Updated 'name' returned correctly")
            else:
                ctx.fail("Updated 'name' mismatch in response")
    else:
        ctx.skip("PUT /api/organizations/:id by owner — seed ID or token not available")

    # 8-auth  PUT without auth → 401
    if organization1_id:
        resp = ctx.req("PUT", "/api/organizations/" + str(organization1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/organizations/{organization1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/organizations/:id without auth — seed ID not available")


    # 8-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/organizations/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/organizations/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/organizations/9999999 — token not available")

    # 8-delete-noauth  DELETE without auth → 401
    if organization2_id:
        resp = ctx.req("DELETE", "/api/organizations/" + str(organization2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/organizations/{organization2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/organizations/:id without auth — seed ID2 not available")


    # 8-delete-owner  DELETE by owner → 204
    if organization2_id and token1:
        resp = ctx.req("DELETE", "/api/organizations/" + str(organization2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/organizations/{organization2_id} by owner → 204"):
            ctx.state["organization2_deleted"] = True
    else:
        ctx.skip("DELETE /api/organizations/:id by owner — seed ID2 or token not available")

    # 8-get-deleted  GET after delete → 404
    if organization2_id and ctx.state.get("organization2_deleted"):
        resp = ctx.req("GET", "/api/organizations/" + str(organization2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/organizations/{organization2_id} after deletion → 404")

    # 8-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/organizations/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/organizations/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/organizations/9999999 — token not available")
