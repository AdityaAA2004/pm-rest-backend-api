"""
Section 23 — Nested routes: GET/POST /api/organizations/:id/projects.

Organization is the primary parent of Project. The organizationId
is injected from the URL param. The None (if present) is injected from JWT.

Populates ctx.state: parent_nested_project_id.
Requires ctx.state:
  user1_id, user1_token, user2_id, user2_token
  organization1_id, organization3_id (from organizations seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("23 · NESTED ROUTES — /api/organizations/:id/projects")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    organization1_id = ctx.state.get("organization1_id")
    organization3_id = ctx.state.get("organization3_id")

    # 23-1  GET → 200 paginated, scoped to parent
    if organization1_id:
        resp = ctx.req("GET",
                       "/api/organizations/" + str(organization1_id) + "/projects")
        if ctx.assert_status(resp, 200,
                             f"GET /api/organizations/{organization1_id}/projects → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/organizations/{organization1_id}/projects")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("organizationId") != organization1_id]
            if wrong:
                ctx.fail(f"projects list contains items for other parents: {wrong}")
            else:
                ctx.ok(f"All projects correctly scoped to organization1")

    # 23-2  GET pagination
    if organization1_id:
        resp = ctx.req("GET",
                       "/api/organizations/" + str(organization1_id) + "/projects",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/organizations/{organization1_id}/projects?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on parent-nested projects")

    # 23-3  Non-existent parent → empty list (not 404)
    resp = ctx.req("GET", "/api/organizations/9999999/projects")
    if ctx.assert_status(resp, 200,
                         "GET /api/organizations/9999999/projects → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent parent's projects returns total=0")

    # 23-4  POST without auth → 401
    if organization1_id:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/projects",
                       body={
                           "name": "Anonymous attempt",
                       })
        ctx.assert_status(resp, 401,
                          f"POST /api/organizations/{organization1_id}/projects without auth → 401",
                          auth_fail=True)

    # 23-5  POST with auth, missing required fields → 400
    if organization1_id and token1:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/projects",
                       token=token1,
                       body={
                       })
        ctx.assert_status(resp, 400,
                          f"POST nested projects missing name → 400")

    # 23-6  POST with auth — organizationId injected from URL
    parent_nested_child_id = None
    if organization1_id and token1:
        resp = ctx.req("POST",
                       "/api/organizations/" + str(organization1_id) + "/projects",
                       token=token1,
                       body={
                           "name": 'Test Name 1',
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested Project (parent-scoped)"):
            data = ctx.safe_json(resp)
            parent_nested_child_id = data.get("id")
            ctx.state["parent_nested_project_id"] = parent_nested_child_id
            if data.get("organizationId") == organization1_id:
                ctx.ok("organizationId injected correctly from URL param")
            else:
                ctx.fail(f"organizationId mismatch: expected {organization1_id}, got {data.get('organizationId')}")

