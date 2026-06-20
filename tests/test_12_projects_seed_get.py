"""
Section 12 — Project: seed data + unauthenticated GET operations.

Creates projects that subsequent sections depend on.

Populates ctx.state: project1_id, project2_id, project3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
  organization1_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("12 · PROJECT — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    organization1_id = ctx.state.get("organization1_id")

    # --- Seed: create projects ---

    _create_path = f"/api/organizations/{organization1_id}/projects"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "name": 'Test Name 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create project1"):
        data = ctx.safe_json(resp)
        ctx.state["project1_id"] = data.get("id")
        if data.get("organizationId") == organization1_id:
            ctx.ok("organizationId injected from URL param")
        else:
            ctx.fail(f"organizationId mismatch: expected {organization1_id}, got {data.get('organizationId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "name": 'Test Name 2',
        "description": 'Test description 2',
        "archived": True,
    })
    if ctx.assert_status(resp, 201, "Seed: Create project2"):
        data = ctx.safe_json(resp)
        ctx.state["project2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "name": 'Test Name 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create project3"):
        data = ctx.safe_json(resp)
        ctx.state["project3_id"] = data.get("id")

    # --- GET tests ---

    # 12-1  Paginated list
    resp = ctx.req("GET", "/api/projects")
    if ctx.assert_status(resp, 200, "GET /api/projects → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/projects")

    # 12-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/projects", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/projects?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 12-3  GET by ID
    project1_id = ctx.state.get("project1_id")
    if project1_id:
        resp = ctx.req("GET", "/api/projects/" + str(project1_id))
        if ctx.assert_status(resp, 200, f"GET /api/projects/{project1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == project1_id:
                ctx.ok("Project id matches requested id")
            else:
                ctx.fail(f"Project id mismatch: {data.get('id')} vs {project1_id}")
    else:
        ctx.skip("GET /api/projects/:id — seed ID not available (seed may have failed)")

    # 12-4  Non-existent → 404
    resp = ctx.req("GET", "/api/projects/9999999")
    ctx.assert_status(resp, 404, "GET /api/projects/9999999 → 404")

    # 12-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/projects/notanid")
    ctx.assert_status(resp, 400, "GET /api/projects/notanid → 400 (invalid ID)")

    # 12-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/projects/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/projects/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/projects/-5 → unexpected HTTP {resp.status_code}")
