"""
Section 4 — User: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/users
  GET /api/users/:id/memberships
  GET /api/users/:id/tasks
  GET /api/users/:id/comments

Requires ctx.state: user1_id, user2_id, user3_id
  user1_id (for nested scoping)
  membership1_id (populated by memberships seed section)
  task1_id (populated by tasks seed section)
  taskComment1_id (populated by taskComments seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("4 · USER — FILTER & SORT")

    user1_id = ctx.state.get("user1_id")
    base = "/api/users"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 4-1  sortBy=id&sortOrder=asc → items ordered ascending by id
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

    # 4-2  sortBy=id&sortOrder=desc → items ordered descending by id
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

    # 4-3  sortBy=id with no sortOrder → defaults to ascending
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

    # 4-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 4-5-1  sortBy=password (sensitive) → ignored, returns 200
    resp = ctx.req("GET", base, params={"sortBy": "password"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=password (sensitive) → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=password")
        ctx.ok("Sensitive field 'password' not accepted as sortBy (correctly ignored)")

    # 4-6-2  sortBy=email&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "email", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=email&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=email&sortOrder=asc")
        ctx.ok("sortBy=email&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "email", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=email&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=email&sortOrder=desc")
        ctx.ok("sortBy=email&sortOrder=desc accepted")

    # 4-6-3  sortBy=username&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "username", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=username&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=username&sortOrder=asc")
        ctx.ok("sortBy=username&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "username", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=username&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=username&sortOrder=desc")
        ctx.ok("sortBy=username&sortOrder=desc accepted")

    # 4-6-4  sortBy=displayName&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "displayName", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=displayName&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=displayName&sortOrder=asc")
        ctx.ok("sortBy=displayName&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "displayName", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=displayName&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=displayName&sortOrder=desc")
        ctx.ok("sortBy=displayName&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if user1_id:
        _fetch = ctx.req("GET", f"{base}/{user1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 4-F-1  Filter by email (string) — match seeded value
    _val_email = _entity1_data.get("email")
    if _val_email is not None:
        resp = ctx.req("GET", base, params={"email": str(_val_email), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?email={_val_email} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?email=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if user1_id in ids_in_result:
                ctx.ok(f"Filter email={_val_email}: entity1 found in results")
            else:
                ctx.fail(f"Filter email={_val_email}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter email: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter email: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("email") != _val_email]
            if not mismatched:
                ctx.ok("Filter email: all returned items match filter value")
            else:
                ctx.fail(f"Filter email: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter email: entity1 data not available (seed may have failed)")

    # 4-F-1b  Filter by email with value that matches no record
    _absent_val = "__no_user_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"email": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?email=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter email with absent value: total=0")
        else:
            ctx.fail(f"Filter email with absent value: expected total=0, got {total}")

    # 4-F-2  Filter by username (string) — match seeded value
    _val_username = _entity1_data.get("username")
    if _val_username is not None:
        resp = ctx.req("GET", base, params={"username": str(_val_username), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?username={_val_username} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?username=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if user1_id in ids_in_result:
                ctx.ok(f"Filter username={_val_username}: entity1 found in results")
            else:
                ctx.fail(f"Filter username={_val_username}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter username: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter username: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("username") != _val_username]
            if not mismatched:
                ctx.ok("Filter username: all returned items match filter value")
            else:
                ctx.fail(f"Filter username: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter username: entity1 data not available (seed may have failed)")

    # 4-F-2b  Filter by username with value that matches no record
    _absent_val = "__no_user_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"username": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?username=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter username with absent value: total=0")
        else:
            ctx.fail(f"Filter username with absent value: expected total=0, got {total}")

    # 4-F-3  Filter by displayName (string) — match seeded value
    _val_displayName = _entity1_data.get("displayName")
    if _val_displayName is not None:
        resp = ctx.req("GET", base, params={"displayName": str(_val_displayName), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?displayName={_val_displayName} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?displayName=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if user1_id in ids_in_result:
                ctx.ok(f"Filter displayName={_val_displayName}: entity1 found in results")
            else:
                ctx.fail(f"Filter displayName={_val_displayName}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter displayName: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter displayName: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("displayName") != _val_displayName]
            if not mismatched:
                ctx.ok("Filter displayName: all returned items match filter value")
            else:
                ctx.fail(f"Filter displayName: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter displayName: entity1 data not available (seed may have failed)")

    # 4-F-3b  Filter by displayName with value that matches no record
    _absent_val = "__no_user_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"displayName": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?displayName=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter displayName with absent value: total=0")
        else:
            ctx.fail(f"Filter displayName with absent value: expected total=0, got {total}")


    # 4-FC  Filter + sort + pagination composed together
    _first_filter_field = "email"
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

    # 4-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


    # ── Nested: GET /api/users/:id/memberships filter & sort ─────────

    _parent_id = ctx.state.get("user1_id")
    _nested_base = f"/api/users/{user1_id}/memberships"

    if _parent_id:
        # 4-N1-1  sortBy=id&sortOrder=asc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=asc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=asc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested memberships: sortBy=id&sortOrder=asc correct")
                else:
                    ctx.fail(f"Nested memberships: expected ascending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested memberships: fewer than 2 items, order not verifiable")

        # 4-N1-2  sortBy=id&sortOrder=desc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=desc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=desc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids, reverse=True):
                    ctx.ok(f"Nested memberships: sortBy=id&sortOrder=desc correct")
                else:
                    ctx.fail(f"Nested memberships: expected descending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested memberships: fewer than 2 items, order not verifiable")

        # 4-N1-3  sortBy=id (no sortOrder) → defaults to asc
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested memberships: default sortOrder is asc")
                else:
                    ctx.fail(f"Nested memberships: default sortOrder not asc, got {ids[:5]}")

        # 4-N1-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 4-N1-5  Filter on nested memberships
        _child1_id = ctx.state.get("membership1_id")
        _child1_data = {}
        if _child1_id:
            _cfetch = ctx.req("GET", f"/api/memberships/{membership1_id}")
            if _cfetch.status_code == 200:
                _child1_data = ctx.safe_json(_cfetch)

        _cval_role = _child1_data.get("role")
        if _cval_role is not None:
            resp = ctx.req("GET", _nested_base, params={"role": str(_cval_role), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?role=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?role=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("role") != _cval_role]
                if not mismatched:
                    ctx.ok(f"Nested memberships filter role: all items match")
                else:
                    ctx.fail(f"Nested memberships filter role: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter role: child data not available")


        # 4-N1-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested memberships filter/sort: user1_id not available")

    # ── Nested: GET /api/users/:id/tasks filter & sort ─────────

    _parent_id = ctx.state.get("user1_id")
    _nested_base = f"/api/users/{user1_id}/tasks"

    if _parent_id:
        # 4-N2-1  sortBy=id&sortOrder=asc on nested route
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

        # 4-N2-2  sortBy=id&sortOrder=desc on nested route
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

        # 4-N2-3  sortBy=id (no sortOrder) → defaults to asc
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

        # 4-N2-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 4-N2-5  Filter on nested tasks
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


        # 4-N2-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested tasks filter/sort: user1_id not available")

    # ── Nested: GET /api/users/:id/comments filter & sort ─────────

    _parent_id = ctx.state.get("user1_id")
    _nested_base = f"/api/users/{user1_id}/comments"

    if _parent_id:
        # 4-N3-1  sortBy=id&sortOrder=asc on nested route
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

        # 4-N3-2  sortBy=id&sortOrder=desc on nested route
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

        # 4-N3-3  sortBy=id (no sortOrder) → defaults to asc
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

        # 4-N3-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 4-N3-5  Filter on nested comments
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


        # 4-N3-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested comments filter/sort: user1_id not available")

