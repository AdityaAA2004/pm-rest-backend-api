"""
Section 13 — Project: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/projects
  GET /api/projects/:id/tasks

Requires ctx.state: project1_id, project2_id, project3_id
  user1_id (for nested scoping)
  task1_id (populated by tasks seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("13 · PROJECT — FILTER & SORT")

    project1_id = ctx.state.get("project1_id")
    base = "/api/projects"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 13-1  sortBy=id&sortOrder=asc → items ordered ascending by id
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

    # 13-2  sortBy=id&sortOrder=desc → items ordered descending by id
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

    # 13-3  sortBy=id with no sortOrder → defaults to ascending
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

    # 13-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 13-6-2  sortBy=name&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "name", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=name&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=name&sortOrder=asc")
        ctx.ok("sortBy=name&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "name", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=name&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=name&sortOrder=desc")
        ctx.ok("sortBy=name&sortOrder=desc accepted")

    # 13-6-3  sortBy=description&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=asc")
        ctx.ok("sortBy=description&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=desc")
        ctx.ok("sortBy=description&sortOrder=desc accepted")

    # 13-6-4  sortBy=archived&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "archived", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=archived&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=archived&sortOrder=asc")
        ctx.ok("sortBy=archived&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "archived", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=archived&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=archived&sortOrder=desc")
        ctx.ok("sortBy=archived&sortOrder=desc accepted")

    # 13-6-5  sortBy=organizationId&sortOrder=asc → 200, valid response
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
    if project1_id:
        _fetch = ctx.req("GET", f"{base}/{project1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 13-F-1  Filter by name (string) — match seeded value
    _val_name = _entity1_data.get("name")
    if _val_name is not None:
        resp = ctx.req("GET", base, params={"name": str(_val_name), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?name={_val_name} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?name=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if project1_id in ids_in_result:
                ctx.ok(f"Filter name={_val_name}: entity1 found in results")
            else:
                ctx.fail(f"Filter name={_val_name}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter name: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter name: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("name") != _val_name]
            if not mismatched:
                ctx.ok("Filter name: all returned items match filter value")
            else:
                ctx.fail(f"Filter name: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter name: entity1 data not available (seed may have failed)")

    # 13-F-1b  Filter by name with value that matches no record
    _absent_val = "__no_project_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"name": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?name=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter name with absent value: total=0")
        else:
            ctx.fail(f"Filter name with absent value: expected total=0, got {total}")

    # 13-F-2  Filter by description (string) — match seeded value
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
            if project1_id in ids_in_result:
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

    # 13-F-2b  Filter by description with value that matches no record
    _absent_val = "__no_project_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"description": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?description=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter description with absent value: total=0")
        else:
            ctx.fail(f"Filter description with absent value: expected total=0, got {total}")

    # 13-F-3  Filter by archived (boolean)
    for _bool_str in ("true", "false"):
        resp = ctx.req("GET", base, params={"archived": _bool_str, "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?archived={_bool_str} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?archived={_bool_str}")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            expected_bool = _bool_str == "true"
            mismatched = [item for item in items if item.get("archived") != expected_bool]
            if not mismatched:
                ctx.ok(f"Filter archived={_bool_str}: all {len(items)} items match")
            else:
                ctx.fail(f"Filter archived={_bool_str}: {len(mismatched)} items have wrong value")
            if total <= _baseline_total:
                ctx.ok(f"Filter archived={_bool_str}: total ({total}) ≤ baseline ({_baseline_total})")

    # 13-F-4  Filter by organizationId (number) — match seeded value
    _val_organizationId = _entity1_data.get("organizationId")
    if _val_organizationId is not None:
        resp = ctx.req("GET", base, params={"organizationId": str(_val_organizationId), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?organizationId={_val_organizationId} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?organizationId=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            ids_in_result = [item.get("id") for item in items]
            if project1_id in ids_in_result:
                ctx.ok(f"Filter organizationId={_val_organizationId}: entity1 found in results")
            else:
                ctx.fail(f"Filter organizationId={_val_organizationId}: entity1 missing from results")
            if total <= _baseline_total:
                ctx.ok(f"Filter organizationId: filtered total ({total}) ≤ baseline ({_baseline_total})")
    else:
        ctx.skip("Filter organizationId: entity1 data not available")


    # 13-FC  Filter + sort + pagination composed together
    _first_filter_field = "name"
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

    # 13-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


    # ── Nested: GET /api/projects/:id/tasks filter & sort ─────────

    _parent_id = ctx.state.get("project1_id")
    _nested_base = f"/api/projects/{project1_id}/tasks"

    if _parent_id:
        # 13-N1-1  sortBy=id&sortOrder=asc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=asc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=asc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested tasks: sortBy=id&sortOrder=asc correct")
                else:
                    ctx.fail(f"Nested tasks: expected ascending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested tasks: fewer than 2 items, order not verifiable")

        # 13-N1-2  sortBy=id&sortOrder=desc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=desc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=desc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids, reverse=True):
                    ctx.ok(f"Nested tasks: sortBy=id&sortOrder=desc correct")
                else:
                    ctx.fail(f"Nested tasks: expected descending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested tasks: fewer than 2 items, order not verifiable")

        # 13-N1-3  sortBy=id (no sortOrder) → defaults to asc
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested tasks: default sortOrder is asc")
                else:
                    ctx.fail(f"Nested tasks: default sortOrder not asc, got {ids[:5]}")

        # 13-N1-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 13-N1-5  Filter on nested tasks
        _child1_id = ctx.state.get("task1_id")
        _child1_data = {}
        if _child1_id:
            _cfetch = ctx.req("GET", f"/api/tasks/{task1_id}")
            if _cfetch.status_code == 200:
                _child1_data = ctx.safe_json(_cfetch)

        _cval_title = _child1_data.get("title")
        if _cval_title is not None:
            resp = ctx.req("GET", _nested_base, params={"title": str(_cval_title), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?title=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?title=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("title") != _cval_title]
                if not mismatched:
                    ctx.ok(f"Nested tasks filter title: all items match")
                else:
                    ctx.fail(f"Nested tasks filter title: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter title: child data not available")

        _cval_description = _child1_data.get("description")
        if _cval_description is not None:
            resp = ctx.req("GET", _nested_base, params={"description": str(_cval_description), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?description=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?description=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("description") != _cval_description]
                if not mismatched:
                    ctx.ok(f"Nested tasks filter description: all items match")
                else:
                    ctx.fail(f"Nested tasks filter description: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter description: child data not available")

        _cval_status = _child1_data.get("status")
        if _cval_status is not None:
            resp = ctx.req("GET", _nested_base, params={"status": str(_cval_status), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?status=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?status=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("status") != _cval_status]
                if not mismatched:
                    ctx.ok(f"Nested tasks filter status: all items match")
                else:
                    ctx.fail(f"Nested tasks filter status: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter status: child data not available")


        # 13-N1-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested tasks filter/sort: project1_id not available")

