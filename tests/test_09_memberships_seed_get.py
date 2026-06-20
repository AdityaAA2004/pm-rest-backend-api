"""
Section 9 — Membership: seed data + unauthenticated GET operations.

Creates memberships that subsequent sections depend on.

Populates ctx.state: membership1_id, membership2_id, membership3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
  organization1_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("9 · MEMBERSHIP — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    organization1_id = ctx.state.get("organization1_id")

    # --- Seed: create memberships ---

    _create_path = f"/api/organizations/{organization1_id}/memberships"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
    })
    if ctx.assert_status(resp, 201, "Seed: Create membership1"):
        data = ctx.safe_json(resp)
        ctx.state["membership1_id"] = data.get("id")
        if data.get("userId") == user1_id:
            ctx.ok("userId injected from JWT")
        else:
            ctx.fail(f"userId mismatch: expected {user1_id}, got {data.get('userId')}")
        if data.get("organizationId") == organization1_id:
            ctx.ok("organizationId injected from URL param")
        else:
            ctx.fail(f"organizationId mismatch: expected {organization1_id}, got {data.get('organizationId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "role": 'member',
    })
    if ctx.assert_status(resp, 201, "Seed: Create membership2"):
        data = ctx.safe_json(resp)
        ctx.state["membership2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
    })
    if ctx.assert_status(resp, 201, "Seed: Create membership3"):
        data = ctx.safe_json(resp)
        ctx.state["membership3_id"] = data.get("id")

    # --- GET tests ---

    # 9-1  Paginated list
    resp = ctx.req("GET", "/api/memberships")
    if ctx.assert_status(resp, 200, "GET /api/memberships → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/memberships")

    # 9-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/memberships", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/memberships?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 9-3  GET by ID
    membership1_id = ctx.state.get("membership1_id")
    if membership1_id:
        resp = ctx.req("GET", "/api/memberships/" + str(membership1_id))
        if ctx.assert_status(resp, 200, f"GET /api/memberships/{membership1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == membership1_id:
                ctx.ok("Membership id matches requested id")
            else:
                ctx.fail(f"Membership id mismatch: {data.get('id')} vs {membership1_id}")
    else:
        ctx.skip("GET /api/memberships/:id — seed ID not available (seed may have failed)")

    # 9-4  Non-existent → 404
    resp = ctx.req("GET", "/api/memberships/9999999")
    ctx.assert_status(resp, 404, "GET /api/memberships/9999999 → 404")

    # 9-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/memberships/notanid")
    ctx.assert_status(resp, 400, "GET /api/memberships/notanid → 400 (invalid ID)")

    # 9-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/memberships/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/memberships/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/memberships/-5 → unexpected HTTP {resp.status_code}")
