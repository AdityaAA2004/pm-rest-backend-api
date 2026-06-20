"""
Section 19 — TaskComment: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/taskComments

Requires ctx.state: taskComment1_id, taskComment2_id, taskComment3_id
  user1_id (for nested scoping)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("19 · TASKCOMMENT — FILTER & SORT")

    taskComment1_id = ctx.state.get("taskComment1_id")
    base = "/api/taskComments"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 19-1  sortBy=id&sortOrder=asc → items ordered ascending by id
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

    # 19-2  sortBy=id&sortOrder=desc → items ordered descending by id
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

    # 19-3  sortBy=id with no sortOrder → defaults to ascending
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

    # 19-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 19-6-2  sortBy=body&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "body", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=body&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=body&sortOrder=asc")
        ctx.ok("sortBy=body&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "body", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=body&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=body&sortOrder=desc")
        ctx.ok("sortBy=body&sortOrder=desc accepted")

    # 19-6-3  sortBy=authorId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "authorId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=authorId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=authorId&sortOrder=asc")
        ctx.ok("sortBy=authorId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "authorId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=authorId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=authorId&sortOrder=desc")
        ctx.ok("sortBy=authorId&sortOrder=desc accepted")

    # 19-6-4  sortBy=taskId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "taskId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=taskId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=taskId&sortOrder=asc")
        ctx.ok("sortBy=taskId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "taskId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=taskId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=taskId&sortOrder=desc")
        ctx.ok("sortBy=taskId&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if taskComment1_id:
        _fetch = ctx.req("GET", f"{base}/{taskComment1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 19-F-1  Filter by body (string) — match seeded value
    _val_body = _entity1_data.get("body")
    if _val_body is not None:
        resp = ctx.req("GET", base, params={"body": str(_val_body), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?body={_val_body} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?body=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if taskComment1_id in ids_in_result:
                ctx.ok(f"Filter body={_val_body}: entity1 found in results")
            else:
                ctx.fail(f"Filter body={_val_body}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter body: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter body: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("body") != _val_body]
            if not mismatched:
                ctx.ok("Filter body: all returned items match filter value")
            else:
                ctx.fail(f"Filter body: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter body: entity1 data not available (seed may have failed)")

    # 19-F-1b  Filter by body with value that matches no record
    _absent_val = "__no_taskComment_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"body": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?body=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter body with absent value: total=0")
        else:
            ctx.fail(f"Filter body with absent value: expected total=0, got {total}")

    # 19-F-2  Filter by authorId (number) — match seeded value
    _val_authorId = _entity1_data.get("authorId")
    if _val_authorId is not None:
        resp = ctx.req("GET", base, params={"authorId": str(_val_authorId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?authorId={_val_authorId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?authorId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if taskComment1_id in ids_in_result:
                ctx.ok(f"Filter authorId={_val_authorId}: entity1 found in results")
            else:
                ctx.fail(f"Filter authorId={_val_authorId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter authorId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter authorId: entity1 data not available")

    # 19-F-3  Filter by taskId (number) — match seeded value
    _val_taskId = _entity1_data.get("taskId")
    if _val_taskId is not None:
        resp = ctx.req("GET", base, params={"taskId": str(_val_taskId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?taskId={_val_taskId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?taskId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if taskComment1_id in ids_in_result:
                ctx.ok(f"Filter taskId={_val_taskId}: entity1 found in results")
            else:
                ctx.fail(f"Filter taskId={_val_taskId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter taskId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter taskId: entity1 data not available")


    # 19-FC  Filter + sort + pagination composed together
    _first_filter_field = "body"
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

    # 19-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


