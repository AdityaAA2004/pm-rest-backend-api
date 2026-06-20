"""
Section 11 — Membership: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  membership1_id, membership2_id, membership3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("11 · MEMBERSHIP — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    membership1_id = ctx.state.get("membership1_id")
    membership2_id = ctx.state.get("membership2_id")
    membership3_id = ctx.state.get("membership3_id")
    organization1_id = ctx.state.get("organization1_id")
    _create_path = f"/api/organizations/{organization1_id}/memberships"

    # 11-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
    })
    ctx.assert_status(resp, 401,
                      "POST /api/organizations/:id/memberships without auth → 401",
                      auth_fail=True)


# LLM_SECTION_START
# Generate required-field validation tests for entity "Membership".
# Canonical create path: /api/organizations/:id/memberships
# Requires authentication: True
#
# Required scalar fields (excluding server-injected FK fields):
#
# If the required fields list above is EMPTY, output only this single comment line and nothing else:
#   # (no required fields to validate)
#
# Otherwise, for EACH required field, generate one test:
#   - Omit only that field from the body
#   - Include all other required fields with sensible values
#   - MUST also include every secondary FK listed below in the body (they are required by the API)
#   - Expect HTTP 400: ctx.assert_status(resp, 400, "POST membership missing <field> → 400")
#   - Wrap in `if token1:` guard
#
# Then generate ONE ownership spoofing test for the owner FK (if present):
#   - Include "userId": <user2_id> in the body while using token1
#   - If response is 201 and data.get("userId") == user1_id: ctx.ok("spoofing prevented")
#   - If response is 201 and data.get("userId") == user2_id: ctx.warn("SECURITY: ownership spoofing succeeded")
#   - Store the created entity id in ctx.state["spoofed_membership_id"] for cleanup
#
# Available variables (already declared above):
#   token1, token2
#   user1_id, user2_id
#   membership1_id, membership2_id, membership3_id
# LLM_SECTION_END    # 11-update  PUT happy path → 200
    if membership1_id and token1:
        _update_val: str | int = "admin"
        resp = ctx.req("PUT", "/api/memberships/" + str(membership1_id),
                       token=token1,
                       body={"role": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/memberships/{membership1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("role") == _update_val:
                ctx.ok("Updated 'role' returned correctly")
            else:
                ctx.fail("Updated 'role' mismatch in response")
    else:
        ctx.skip("PUT /api/memberships/:id by owner — seed ID or token not available")

    # 11-auth  PUT without auth → 401
    if membership1_id:
        resp = ctx.req("PUT", "/api/memberships/" + str(membership1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/memberships/{membership1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/memberships/:id without auth — seed ID not available")

    # 11-owner  PUT by non-owner → 403
    if membership1_id and token2:
        resp = ctx.req("PUT", "/api/memberships/" + str(membership1_id),
                       token=token2,
                       body={"title": "Hijack attempt"})
        ctx.assert_status(resp, 403,
                          f"PUT /api/memberships/{membership1_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/memberships/:id by non-owner — seed ID or token2 not available")

    # 11-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/memberships/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/memberships/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/memberships/9999999 — token not available")

    # 11-delete-noauth  DELETE without auth → 401
    if membership2_id:
        resp = ctx.req("DELETE", "/api/memberships/" + str(membership2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/memberships/{membership2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/memberships/:id without auth — seed ID2 not available")

    # 11-delete-nonowner  DELETE by non-owner → 403
    if membership2_id and token2:
        resp = ctx.req("DELETE", "/api/memberships/" + str(membership2_id),
                       token=token2)
        ctx.assert_status(resp, 403,
                          f"DELETE /api/memberships/{membership2_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/memberships/:id by non-owner — seed ID2 or token2 not available")

    # 11-delete-owner  DELETE by owner → 204
    if membership2_id and token1:
        resp = ctx.req("DELETE", "/api/memberships/" + str(membership2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/memberships/{membership2_id} by owner → 204"):
            ctx.state["membership2_deleted"] = True
    else:
        ctx.skip("DELETE /api/memberships/:id by owner — seed ID2 or token not available")

    # 11-get-deleted  GET after delete → 404
    if membership2_id and ctx.state.get("membership2_deleted"):
        resp = ctx.req("GET", "/api/memberships/" + str(membership2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/memberships/{membership2_id} after deletion → 404")

    # 11-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/memberships/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/memberships/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/memberships/9999999 — token not available")
