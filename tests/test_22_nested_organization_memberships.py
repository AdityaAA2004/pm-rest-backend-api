"""
Section 22 — Nested routes: GET/POST /api/organizations/:id/memberships.

Organization is the primary parent of Membership. The organizationId
is injected from the URL param. The userId (if present) is injected from JWT.

Populates ctx.state: parent_nested_membership_id.
Requires ctx.state:
  user1_id, user1_token, user2_id, user2_token
  organization1_id, organization3_id (from organizations seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("22 · NESTED ROUTES — /api/organizations/:id/memberships")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    organization1_id = ctx.state.get("organization1_id")
    organization3_id = ctx.state.get("organization3_id")

    # 22-1  GET → 200 paginated, scoped to parent
    if organization1_id:
        resp = ctx.req("GET",
                       "/api/organizations/" + str(organization1_id) + "/memberships")
        if ctx.assert_status(resp, 200,
                             f"GET /api/organizations/{organization1_id}/memberships → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/organizations/{organization1_id}/memberships")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("organizationId") != organization1_id]
            if wrong:
                ctx.fail(f"memberships list contains items for other parents: {wrong}")
            else:
                ctx.ok(f"All memberships correctly scoped to organization1")

    # 22-2  GET pagination
    if organization1_id:
        resp = ctx.req("GET",
                       "/api/organizations/" + str(organization1_id) + "/memberships",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/organizations/{organization1_id}/memberships?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on parent-nested memberships")

    # 22-3  Non-existent parent → empty list (not 404)
    resp = ctx.req("GET", "/api/organizations/9999999/memberships")
    if ctx.assert_status(resp, 200,
                         "GET /api/organizations/9999999/memberships → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent parent's memberships returns total=0")

    # 22-4  POST without auth → 401
    if organization1_id:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/memberships",
                       body={
                       })
        ctx.assert_status(resp, 401,
                          f"POST /api/organizations/{organization1_id}/memberships without auth → 401",
                          auth_fail=True)

    # 22-5  POST with auth, missing required fields → 400

    # 22-6  POST with auth — organizationId injected from URL
    parent_nested_child_id = None
    if organization1_id and token1:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/memberships",
                       token=token1,
                       body={
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested Membership (parent-scoped)"):
            data = ctx.safe_json(resp)
            parent_nested_child_id = data.get("id")
            ctx.state["parent_nested_membership_id"] = parent_nested_child_id
            if data.get("organizationId") == organization1_id:
                ctx.ok("organizationId injected correctly from URL param")
            else:
                ctx.fail(f"organizationId mismatch: expected {organization1_id}, got {data.get('organizationId')}")
            if data.get("userId") == user1_id:
                ctx.ok("userId injected correctly from JWT")
            else:
                ctx.fail(f"userId mismatch: expected {user1_id}, got {data.get('userId')}")

    # 22-7  Security: owner FK spoofing via nested route
    if organization1_id and token1 and user2_id:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/memberships",
                       token=token1,
                       body={
                           "userId": "SPOOFED_VALUE",
                       })
        if resp.status_code == 201:
            data = ctx.safe_json(resp)
            spoofed_id = ctx.state.get("parent_nested_membership_id")
            if data.get("userId") == user2_id:
                ctx.warn(
                    f"SECURITY: POST /api/organizations/:id/memberships allows arbitrary userId — "
                    "should inject from JWT instead."
                )
                ctx.state["spoofed_membership_id"] = data.get("id")
            elif data.get("userId") == user1_id:
                ctx.ok("POST nested: userId spoof ignored, set from token")
