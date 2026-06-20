"""
Section 6 — Organization: seed data + unauthenticated GET operations.

Creates organizations that subsequent sections depend on.

Populates ctx.state: organization1_id, organization2_id, organization3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("6 · ORGANIZATION — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")

    # --- Seed: create organizations ---

    _create_path = "/api/organizations"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "name": 'Test Name 1',
        "slug": 'test-slug-1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create organization1"):
        data = ctx.safe_json(resp)
        ctx.state["organization1_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "name": 'Test Name 2',
        "slug": 'test-slug-2',
        "description": 'Test description 2',
        "website": 'https://example.com/2',
    })
    if ctx.assert_status(resp, 201, "Seed: Create organization2"):
        data = ctx.safe_json(resp)
        ctx.state["organization2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "name": 'Test Name 3',
        "slug": 'test-slug-3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create organization3"):
        data = ctx.safe_json(resp)
        ctx.state["organization3_id"] = data.get("id")

    # --- GET tests ---

    # 6-1  Paginated list
    resp = ctx.req("GET", "/api/organizations")
    if ctx.assert_status(resp, 200, "GET /api/organizations → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/organizations")

    # 6-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/organizations", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/organizations?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 6-3  GET by ID
    organization1_id = ctx.state.get("organization1_id")
    if organization1_id:
        resp = ctx.req("GET", "/api/organizations/" + str(organization1_id))
        if ctx.assert_status(resp, 200, f"GET /api/organizations/{organization1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == organization1_id:
                ctx.ok("Organization id matches requested id")
            else:
                ctx.fail(f"Organization id mismatch: {data.get('id')} vs {organization1_id}")
    else:
        ctx.skip("GET /api/organizations/:id — seed ID not available (seed may have failed)")

    # 6-4  Non-existent → 404
    resp = ctx.req("GET", "/api/organizations/9999999")
    ctx.assert_status(resp, 404, "GET /api/organizations/9999999 → 404")

    # 6-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/organizations/notanid")
    ctx.assert_status(resp, 400, "GET /api/organizations/notanid → 400 (invalid ID)")

    # 6-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/organizations/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/organizations/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/organizations/-5 → unexpected HTTP {resp.status_code}")
