"""
Section 27 — Input validation and edge cases.

Uses Organization as the primary test entity.
Requires ctx.state: user1_token.
Populates ctx.state: long_title_organization_id, xss_organization_id, unicode_organization_id
                     (kept for cleanup).
"""

import requests as _req
from helpers import TestContext, section

def run(ctx: TestContext) -> None:
    section("27 · INPUT VALIDATION & EDGE CASES")

    token1 = ctx.state.get("user1_token")

    # Resolve canonical create path — replace :id placeholder with actual parent ID from state
    _create_path = "/api/organizations"


    # 27-1  Very long name (300 chars) — should be rejected or truncated
    long_value = "A" * 300
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "name": long_value,
                           "slug": "Normal value",
                       })
        if resp.status_code in (400, 422):
            ctx.ok(f"POST organization name=300 chars → HTTP {resp.status_code} (rejected)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST organization accepted 300-char name — "
                "consider .max(255) in the Zod 'name' schema"
            )
            ctx.state["long_title_organization_id"] = ctx.safe_json(resp).get("id")

    # 27-2  Very long slug (15 000 chars)
    long_content = "C" * 15_000
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "slug": long_content,
                           "name": "Normal value",
                       })
        if resp.status_code in (400, 422):
            ctx.ok(f"POST organization slug=15000 chars → HTTP {resp.status_code} (rejected)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST organization accepted 15 000-char slug — "
                "consider .max(10000) in the Zod schema"
            )
            ctx.state["long_content_organization_id"] = ctx.safe_json(resp).get("id")

    # 27-3  XSS payload in content — stored verbatim (escaping is frontend responsibility)
    xss_payload = '<script>alert("xss")</script>'
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "name": "XSS Test",
                           "slug": xss_payload,
                       })
        if resp.status_code == 201:
            ctx.warn(
                "XSS payload stored verbatim in DB — ensure HTML escaping is applied "
                "at render time (frontend responsibility)."
            )
            ctx.ok("API stored content without modification (escaping is frontend concern)")
            ctx.state["xss_organization_id"] = ctx.safe_json(resp).get("id")
        else:
            ctx.ok(f"XSS payload rejected with HTTP {resp.status_code}")

    # 27-4  SQL injection in query param — server must not crash
    resp = ctx.req("GET", "/api/organizations", params={"page": "1; DROP TABLE organizations; --"})
    if resp.status_code == 200:
        ctx.ok("SQL injection in ?page param → 200 (gracefully handled / Prisma parameterised)")
    elif resp.status_code == 400:
        ctx.ok("SQL injection in ?page param → 400 (rejected by validation)")
    else:
        ctx.warn(f"SQL injection in page param → unexpected HTTP {resp.status_code}")

    # 27-5  SQL injection in path segment → 400 or 404
    resp = ctx.req("GET", "/api/organizations/1; DROP TABLE organizations --")
    if resp.status_code in (400, 404):
        ctx.ok(f"SQL injection in path segment → HTTP {resp.status_code} (handled)")
    else:
        ctx.warn(f"SQL injection in path segment → unexpected HTTP {resp.status_code}")

    # 27-6  Unicode / emoji — should round-trip correctly
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "name": "Unicode Test 🌍🚀",
                           "slug": "unicode-test-slug",
                       })
        if ctx.assert_status(resp, 201, "POST organization with Unicode/emoji → 201"):
            data = ctx.safe_json(resp)
            content_val = data.get("name", "")
            if "🌍" in content_val or "🚀" in content_val:
                ctx.ok("Unicode/emoji stored and returned correctly")
            else:
                ctx.fail("Emoji not present in returned response (field: name)")
            ctx.state["unicode_organization_id"] = data.get("id")

    # 27-7  Empty string name → 400 (validation)
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "name": "",
                           "slug": "Normal value",
                       })
        if resp.status_code == 400:
            ctx.ok("POST organization with empty string name → 400 (validation)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST organization accepted empty string name — "
                "consider .min(1) in the Zod 'name' schema"
            )

    # 27-8  Non-numeric pagination params → fall back to defaults
    resp = ctx.req("GET", "/api/organizations", params={"page": "abc", "limit": "xyz"})
    if ctx.assert_status(resp, 200, "GET /api/organizations?page=abc&limit=xyz → 200 (defaults)"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 1 and meta.get("limit") == 20:
            ctx.ok("Non-numeric pagination params fall back to defaults page=1 limit=20")
        else:
            ctx.warn(f"Non-numeric pagination produced unexpected meta: {meta}")

    # 27-9  Integer overflow in ID
    big_id = 2 ** 53
    resp = ctx.req("GET", f"/api/organizations/{big_id}")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/organizations/{big_id} (integer overflow) → HTTP {resp.status_code} (handled)")
    else:
        ctx.warn(f"Integer overflow in ID → unexpected HTTP {resp.status_code}")

    # 27-10  Content-Type: text/plain body → 400 or 415
    if token1:
        url = f"{ctx.base_url}{_create_path}"
        print(f"  🚀  POST /api/organizations (Content-Type: text/plain)")
        try:
            resp = _req.post(
                url,
                headers={"Authorization": f"Bearer {token1}", "Content-Type": "text/plain"},
                data='{"name":"value"}',
                timeout=10,
            )
            if resp.status_code in (400, 415):
                ctx.ok(f"POST with Content-Type: text/plain → HTTP {resp.status_code} (non-JSON body rejected)")
            else:
                ctx.warn(
                    f"POST with Content-Type: text/plain → HTTP {resp.status_code} "
                    "— Express json() middleware may have silently ignored the body"
                )
        except Exception as exc:
            ctx.fail(f"Request failed: {exc}")

    # 27-11  No body at all → 400
    if token1:
        url = f"{ctx.base_url}{_create_path}"
        print("  🚀  POST /api/organizations (no body at all)")
        try:
            resp = _req.post(
                url,
                headers={"Authorization": f"Bearer {token1}", "Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (400, 422):
                ctx.ok(f"POST with no body → HTTP {resp.status_code} (validation rejected)")
            else:
                ctx.warn(f"POST with no body → HTTP {resp.status_code}")
        except Exception as exc:
            ctx.fail(f"Request failed: {exc}")
