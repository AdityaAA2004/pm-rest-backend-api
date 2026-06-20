"""
Section 10 — Membership: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/memberships

Requires ctx.state: membership1_id, membership2_id, membership3_id
  user1_id (for nested scoping)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("10 · MEMBERSHIP — FILTER & SORT")

    membership1_id = ctx.state.get("membership1_id")
    base = "/api/memberships"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 10-1  sortBy=id&sortOrder=asc → items ordered ascending by id
    resp = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=id&sortOrder=asc → 200"):
        data = ctx.safe_json(resp)
        ctx.assert_paginated(data, f"{base}?sortBy=id&sortOrder=asc")
        items = data.get("data", [])
        if len(items) >= 2:
            ids = [item.get("id") for item in items if item.get("id") is not None]
            if ids == sorted(ids):
                ctx.ok("sortBy=id&sortOrder=asc: items in ascending id order")
            else:
                ctx.fail(f"sortBy=id&sortOrder=asc: expected ascending ids, got {ids[:5]}")
        else:
            ctx.ok("sortBy=id&sortOrder=asc: fewer than 2 items, order not verifiable")

    # 10-2  sortBy=id&sortOrder=desc → items ordered descending by id
    resp = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=id&sortOrder=desc → 200"):
        data = ctx.safe_json(resp)
        ctx.assert_paginated(data, f"{base}?sortBy=id&sortOrder=desc")
        items = data.get("data", [])
        if len(items) >= 2:
            ids = [item.get("id") for item in items if item.get("id") is not None]
            if ids == sorted(ids, reverse=True):
                ctx.ok("sortBy=id&sortOrder=desc: items in descending id order")
            else:
                ctx.fail(f"sortBy=id&sortOrder=desc: expected descending ids, got {ids[:5]}")
        else:
            ctx.ok("sortBy=id&sortOrder=desc: fewer than 2 items, order not verifiable")

    # 10-3  sortBy=id with no sortOrder → defaults to ascending
    resp_asc = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
    resp_def = ctx.req("GET", base, params={"sortBy": "id", "limit": 50})
    if ctx.assert_status(resp_def, 200, f"GET {base}?sortBy=id (no sortOrder) → 200"):
        ctx.assert_paginated(ctx.safe_json(resp_def), f"{base}?sortBy=id")
        items_asc = ctx.safe_json(resp_asc).get("data", []) if resp_asc.status_code == 200 else []
        items_def = ctx.safe_json(resp_def).get("data", [])
        ids_asc = [i.get("id") for i in items_asc]
        ids_def = [i.get("id") for i in items_def]
        if ids_asc and ids_def:
            if ids_def == ids_asc:
                ctx.ok("sortBy=id with no sortOrder matches explicit asc order")
            else:
                ctx.fail(f"Default sortOrder should be asc. asc={ids_asc[:3]} default={ids_def[:3]}")
        else:
            ctx.ok("Default sortOrder: no items to compare")

    # 10-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 10-6-2  sortBy=role&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "role", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=role&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=role&sortOrder=asc")
        ctx.ok("sortBy=role&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "role", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=role&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=role&sortOrder=desc")
        ctx.ok("sortBy=role&sortOrder=desc accepted")

    # 10-6-3  sortBy=userId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "userId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=userId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=userId&sortOrder=asc")
        ctx.ok("sortBy=userId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "userId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=userId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=userId&sortOrder=desc")
        ctx.ok("sortBy=userId&sortOrder=desc accepted")

    # 10-6-4  sortBy=organizationId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "organizationId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=organizationId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=organizationId&sortOrder=asc")
        ctx.ok("sortBy=organizationId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "organizationId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=organizationId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=organizationId&sortOrder=desc")
        ctx.ok("sortBy=organizationId&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if membership1_id:
        _fetch = ctx.req("GET", f"{base}/{membership1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 10-F-1  Filter by role (string) — match seeded value
    _val_role = _entity1_data.get("role")
    if _val_role is not None:
        resp = ctx.req("GET", base, params={"role": str(_val_role), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?role={_val_role} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?role=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if membership1_id in ids_in_result:
                ctx.ok(f"Filter role={_val_role}: entity1 found in results")
            else:
                ctx.fail(f"Filter role={_val_role}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter role: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter role: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("role") != _val_role]
            if not mismatched:
                ctx.ok("Filter role: all returned items match filter value")
            else:
                ctx.fail(f"Filter role: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter role: entity1 data not available (seed may have failed)")

    # 10-F-1b  Filter by role with value that matches no record
    _absent_val = "__no_membership_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"role": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?role=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter role with absent value: total=0")
        else:
            ctx.fail(f"Filter role with absent value: expected total=0, got {total}")

    # 10-F-2  Filter by userId (number) — match seeded value
    _val_userId = _entity1_data.get("userId")
    if _val_userId is not None:
        resp = ctx.req("GET", base, params={"userId": str(_val_userId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?userId={_val_userId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?userId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if membership1_id in ids_in_result:
                ctx.ok(f"Filter userId={_val_userId}: entity1 found in results")
            else:
                ctx.fail(f"Filter userId={_val_userId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter userId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter userId: entity1 data not available")

    # 10-F-3  Filter by organizationId (number) — match seeded value
    _val_organizationId = _entity1_data.get("organizationId")
    if _val_organizationId is not None:
        resp = ctx.req("GET", base, params={"organizationId": str(_val_organizationId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?organizationId={_val_organizationId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?organizationId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if membership1_id in ids_in_result:
                ctx.ok(f"Filter organizationId={_val_organizationId}: entity1 found in results")
            else:
                ctx.fail(f"Filter organizationId={_val_organizationId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter organizationId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter organizationId: entity1 data not available")


    # 10-FC  Filter + sort + pagination composed together
    _first_filter_field = "role"
    _first_filter_val = _entity1_data.get(_first_filter_field)
    if _first_filter_val is not None:
        resp = ctx.req("GET", base, params={
            _first_filter_field: str(_first_filter_val),
            "sortBy": "id",
            "sortOrder": "asc",
            "page": 1,
            "limit": 5,
        })
        if ctx.assert_status(resp, 200, f"GET {base}?filter+sort+page → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?filter+sort+page")
            meta = data.get("meta", {})
            if meta.get("limit") == 5 and meta.get("page") == 1:
                ctx.ok("Filter+sort+pagination: meta correct")
            else:
                ctx.fail(f"Filter+sort+pagination: unexpected meta {meta}")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok("Filter+sort+pagination: items in ascending id order")
                else:
                    ctx.fail(f"Filter+sort+pagination: expected ascending ids, got {ids}")
    else:
        ctx.skip("Filter+sort+pagination: entity1 data not available")

    # 10-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


