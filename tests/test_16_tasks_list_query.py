"""
Section 16 — Task: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/tasks
  GET /api/tasks/:id/comments

Requires ctx.state: task1_id, task2_id, task3_id
  user1_id (for nested scoping)
  taskComment1_id (populated by taskComments seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("16 · TASK — FILTER & SORT")

    task1_id = ctx.state.get("task1_id")
    base = "/api/tasks"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 16-1  sortBy=id&sortOrder=asc → items ordered ascending by id
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

    # 16-2  sortBy=id&sortOrder=desc → items ordered descending by id
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

    # 16-3  sortBy=id with no sortOrder → defaults to ascending
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

    # 16-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 16-6-2  sortBy=title&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "title", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=title&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=title&sortOrder=asc")
        ctx.ok("sortBy=title&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "title", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=title&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=title&sortOrder=desc")
        ctx.ok("sortBy=title&sortOrder=desc accepted")

    # 16-6-3  sortBy=description&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=asc")
        ctx.ok("sortBy=description&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=desc")
        ctx.ok("sortBy=description&sortOrder=desc accepted")

    # 16-6-4  sortBy=status&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "status", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=status&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=status&sortOrder=asc")
        ctx.ok("sortBy=status&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "status", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=status&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=status&sortOrder=desc")
        ctx.ok("sortBy=status&sortOrder=desc accepted")

    # 16-6-5  sortBy=priority&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "priority", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=priority&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=priority&sortOrder=asc")
        ctx.ok("sortBy=priority&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "priority", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=priority&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=priority&sortOrder=desc")
        ctx.ok("sortBy=priority&sortOrder=desc accepted")

    # 16-6-6  sortBy=projectId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "projectId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=projectId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=projectId&sortOrder=asc")
        ctx.ok("sortBy=projectId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "projectId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=projectId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=projectId&sortOrder=desc")
        ctx.ok("sortBy=projectId&sortOrder=desc accepted")

    # 16-6-7  sortBy=assigneeId&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "assigneeId", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=assigneeId&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=assigneeId&sortOrder=asc")
        ctx.ok("sortBy=assigneeId&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "assigneeId", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=assigneeId&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=assigneeId&sortOrder=desc")
        ctx.ok("sortBy=assigneeId&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if task1_id:
        _fetch = ctx.req("GET", f"{base}/{task1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 16-F-1  Filter by title (string) — match seeded value
    _val_title = _entity1_data.get("title")
    if _val_title is not None:
        resp = ctx.req("GET", base, params={"title": str(_val_title), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?title={_val_title} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?title=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter title={_val_title}: entity1 found in results")
            else:
                ctx.fail(f"Filter title={_val_title}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter title: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter title: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("title") != _val_title]
            if not mismatched:
                ctx.ok("Filter title: all returned items match filter value")
            else:
                ctx.fail(f"Filter title: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter title: entity1 data not available (seed may have failed)")

    # 16-F-1b  Filter by title with value that matches no record
    _absent_val = "__no_task_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"title": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?title=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter title with absent value: total=0")
        else:
            ctx.fail(f"Filter title with absent value: expected total=0, got {total}")

    # 16-F-2  Filter by description (string) — match seeded value
    _val_description = _entity1_data.get("description")
    if _val_description is not None:
        resp = ctx.req("GET", base, params={"description": str(_val_description), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?description={_val_description} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?description=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter description={_val_description}: entity1 found in results")
            else:
                ctx.fail(f"Filter description={_val_description}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter description: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter description: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("description") != _val_description]
            if not mismatched:
                ctx.ok("Filter description: all returned items match filter value")
            else:
                ctx.fail(f"Filter description: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter description: entity1 data not available (seed may have failed)")

    # 16-F-2b  Filter by description with value that matches no record
    _absent_val = "__no_task_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"description": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?description=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter description with absent value: total=0")
        else:
            ctx.fail(f"Filter description with absent value: expected total=0, got {total}")

    # 16-F-3  Filter by status (string) — match seeded value
    _val_status = _entity1_data.get("status")
    if _val_status is not None:
        resp = ctx.req("GET", base, params={"status": str(_val_status), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?status={_val_status} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?status=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter status={_val_status}: entity1 found in results")
            else:
                ctx.fail(f"Filter status={_val_status}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter status: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter status: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("status") != _val_status]
            if not mismatched:
                ctx.ok("Filter status: all returned items match filter value")
            else:
                ctx.fail(f"Filter status: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter status: entity1 data not available (seed may have failed)")

    # 16-F-3b  Filter by status with value that matches no record
    _absent_val = "__no_task_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"status": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?status=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter status with absent value: total=0")
        else:
            ctx.fail(f"Filter status with absent value: expected total=0, got {total}")

    # 16-F-4  Filter by priority (number) — match seeded value
    _val_priority = _entity1_data.get("priority")
    if _val_priority is not None:
        resp = ctx.req("GET", base, params={"priority": str(_val_priority), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?priority={_val_priority} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?priority=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter priority={_val_priority}: entity1 found in results")
            else:
                ctx.fail(f"Filter priority={_val_priority}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter priority: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter priority: entity1 data not available")

    # 16-F-5  Filter by projectId (number) — match seeded value
    _val_projectId = _entity1_data.get("projectId")
    if _val_projectId is not None:
        resp = ctx.req("GET", base, params={"projectId": str(_val_projectId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?projectId={_val_projectId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?projectId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter projectId={_val_projectId}: entity1 found in results")
            else:
                ctx.fail(f"Filter projectId={_val_projectId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter projectId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter projectId: entity1 data not available")

    # 16-F-6  Filter by assigneeId (number) — match seeded value
    _val_assigneeId = _entity1_data.get("assigneeId")
    if _val_assigneeId is not None:
        resp = ctx.req("GET", base, params={"assigneeId": str(_val_assigneeId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?assigneeId={_val_assigneeId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?assigneeId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if task1_id in ids_in_result:
                ctx.ok(f"Filter assigneeId={_val_assigneeId}: entity1 found in results")
            else:
                ctx.fail(f"Filter assigneeId={_val_assigneeId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter assigneeId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter assigneeId: entity1 data not available")


    # 16-FC  Filter + sort + pagination composed together
    _first_filter_field = "title"
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

    # 16-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


    # ── Nested: GET /api/tasks/:id/comments filter & sort ─────────

    _parent_id = ctx.state.get("task1_id")
    _nested_base = f"/api/tasks/{task1_id}/comments"

    if _parent_id:
        # 16-N1-1  sortBy=id&sortOrder=asc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=asc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=asc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested comments: sortBy=id&sortOrder=asc correct")
                else:
                    ctx.fail(f"Nested comments: expected ascending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested comments: fewer than 2 items, order not verifiable")

        # 16-N1-2  sortBy=id&sortOrder=desc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=desc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=desc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids, reverse=True):
                    ctx.ok(f"Nested comments: sortBy=id&sortOrder=desc correct")
                else:
                    ctx.fail(f"Nested comments: expected descending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested comments: fewer than 2 items, order not verifiable")

        # 16-N1-3  sortBy=id (no sortOrder) → defaults to asc
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested comments: default sortOrder is asc")
                else:
                    ctx.fail(f"Nested comments: default sortOrder not asc, got {ids[:5]}")

        # 16-N1-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 16-N1-5  Filter on nested comments
        _child1_id = ctx.state.get("taskComment1_id")
        _child1_data = {}
        if _child1_id:
            _cfetch = ctx.req("GET", f"/api/taskComments/{taskComment1_id}")
            if _cfetch.status_code == 200:
                _child1_data = ctx.safe_json(_cfetch)

        _cval_body = _child1_data.get("body")
        if _cval_body is not None:
            resp = ctx.req("GET", _nested_base, params={"body": str(_cval_body), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?body=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?body=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("body") != _cval_body]
                if not mismatched:
                    ctx.ok(f"Nested comments filter body: all items match")
                else:
                    ctx.fail(f"Nested comments filter body: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter body: child data not available")


        # 16-N1-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested comments filter/sort: task1_id not available")

