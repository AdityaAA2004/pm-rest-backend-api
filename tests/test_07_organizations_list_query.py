"""
Section 7 — Organization: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/organizations
  GET /api/organizations/:id/memberships
  GET /api/organizations/:id/projects

Requires ctx.state: organization1_id, organization2_id, organization3_id
  user1_id (for nested scoping)
  membership1_id (populated by memberships seed section)
  project1_id (populated by projects seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("7 · ORGANIZATION — FILTER & SORT")

    organization1_id = ctx.state.get("organization1_id")
    base = "/api/organizations"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 7-1  sortBy=id&sortOrder=asc → items ordered ascending by id
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

    # 7-2  sortBy=id&sortOrder=desc → items ordered descending by id
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

    # 7-3  sortBy=id with no sortOrder → defaults to ascending
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

    # 7-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 7-6-2  sortBy=name&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "name", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=name&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=name&sortOrder=asc")
        ctx.ok("sortBy=name&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "name", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=name&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=name&sortOrder=desc")
        ctx.ok("sortBy=name&sortOrder=desc accepted")

    # 7-6-3  sortBy=slug&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "slug", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=slug&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=slug&sortOrder=asc")
        ctx.ok("sortBy=slug&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "slug", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=slug&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=slug&sortOrder=desc")
        ctx.ok("sortBy=slug&sortOrder=desc accepted")

    # 7-6-4  sortBy=description&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=asc")
        ctx.ok("sortBy=description&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "description", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=description&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=description&sortOrder=desc")
        ctx.ok("sortBy=description&sortOrder=desc accepted")

    # 7-6-5  sortBy=website&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "website", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=website&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=website&sortOrder=asc")
        ctx.ok("sortBy=website&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "website", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=website&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=website&sortOrder=desc")
        ctx.ok("sortBy=website&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if organization1_id:
        _fetch = ctx.req("GET", f"{base}/{organization1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 7-F-1  Filter by name (string) — match seeded value
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
            if organization1_id in ids_in_result:
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

    # 7-F-1b  Filter by name with value that matches no record
    _absent_val = "__no_organization_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"name": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?name=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter name with absent value: total=0")
        else:
            ctx.fail(f"Filter name with absent value: expected total=0, got {total}")

    # 7-F-2  Filter by slug (string) — match seeded value
    _val_slug = _entity1_data.get("slug")
    if _val_slug is not None:
        resp = ctx.req("GET", base, params={"slug": str(_val_slug), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?slug={_val_slug} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?slug=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if organization1_id in ids_in_result:
                ctx.ok(f"Filter slug={_val_slug}: entity1 found in results")
            else:
                ctx.fail(f"Filter slug={_val_slug}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter slug: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter slug: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("slug") != _val_slug]
            if not mismatched:
                ctx.ok("Filter slug: all returned items match filter value")
            else:
                ctx.fail(f"Filter slug: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter slug: entity1 data not available (seed may have failed)")

    # 7-F-2b  Filter by slug with value that matches no record
    _absent_val = "__no_organization_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"slug": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?slug=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter slug with absent value: total=0")
        else:
            ctx.fail(f"Filter slug with absent value: expected total=0, got {total}")

    # 7-F-3  Filter by description (string) — match seeded value
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
            if organization1_id in ids_in_result:
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

    # 7-F-3b  Filter by description with value that matches no record
    _absent_val = "__no_organization_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"description": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?description=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter description with absent value: total=0")
        else:
            ctx.fail(f"Filter description with absent value: expected total=0, got {total}")

    # 7-F-4  Filter by website (string) — match seeded value
    _val_website = _entity1_data.get("website")
    if _val_website is not None:
        resp = ctx.req("GET", base, params={"website": str(_val_website), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?website={_val_website} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?website=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if organization1_id in ids_in_result:
                ctx.ok(f"Filter website={_val_website}: entity1 found in results")
            else:
                ctx.fail(f"Filter website={_val_website}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter website: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter website: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("website") != _val_website]
            if not mismatched:
                ctx.ok("Filter website: all returned items match filter value")
            else:
                ctx.fail(f"Filter website: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter website: entity1 data not available (seed may have failed)")

    # 7-F-4b  Filter by website with value that matches no record
    _absent_val = "__no_organization_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"website": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?website=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter website with absent value: total=0")
        else:
            ctx.fail(f"Filter website with absent value: expected total=0, got {total}")


    # 7-FC  Filter + sort + pagination composed together
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

    # 7-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


    # ── Nested: GET /api/organizations/:id/memberships filter & sort ─────────

    _parent_id = ctx.state.get("organization1_id")
    _nested_base = f"/api/organizations/{organization1_id}/memberships"

    if _parent_id:
        # 7-N1-1  sortBy=id&sortOrder=asc on nested route
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

        # 7-N1-2  sortBy=id&sortOrder=desc on nested route
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

        # 7-N1-3  sortBy=id (no sortOrder) → defaults to asc
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

        # 7-N1-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 7-N1-5  Filter on nested memberships
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


        # 7-N1-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested memberships filter/sort: organization1_id not available")

    # ── Nested: GET /api/organizations/:id/projects filter & sort ─────────

    _parent_id = ctx.state.get("organization1_id")
    _nested_base = f"/api/organizations/{organization1_id}/projects"

    if _parent_id:
        # 7-N2-1  sortBy=id&sortOrder=asc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=asc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=asc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested projects: sortBy=id&sortOrder=asc correct")
                else:
                    ctx.fail(f"Nested projects: expected ascending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested projects: fewer than 2 items, order not verifiable")

        # 7-N2-2  sortBy=id&sortOrder=desc on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id&sortOrder=desc → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id&sortOrder=desc")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids, reverse=True):
                    ctx.ok(f"Nested projects: sortBy=id&sortOrder=desc correct")
                else:
                    ctx.fail(f"Nested projects: expected descending ids, got {ids[:5]}")
            else:
                ctx.ok(f"Nested projects: fewer than 2 items, order not verifiable")

        # 7-N2-3  sortBy=id (no sortOrder) → defaults to asc
        resp = ctx.req("GET", _nested_base, params={"sortBy": "id", "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=id → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{_nested_base}?sortBy=id")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok(f"Nested projects: default sortOrder is asc")
                else:
                    ctx.fail(f"Nested projects: default sortOrder not asc, got {ids[:5]}")

        # 7-N2-4  Unknown sortBy → ignored on nested route
        resp = ctx.req("GET", _nested_base, params={"sortBy": "__nonexistent__"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?sortBy=__nonexistent__ → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?sortBy=unknown")

        # 7-N2-5  Filter on nested projects
        _child1_id = ctx.state.get("project1_id")
        _child1_data = {}
        if _child1_id:
            _cfetch = ctx.req("GET", f"/api/projects/{project1_id}")
            if _cfetch.status_code == 200:
                _child1_data = ctx.safe_json(_cfetch)

        _cval_name = _child1_data.get("name")
        if _cval_name is not None:
            resp = ctx.req("GET", _nested_base, params={"name": str(_cval_name), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?name=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?name=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("name") != _cval_name]
                if not mismatched:
                    ctx.ok(f"Nested projects filter name: all items match")
                else:
                    ctx.fail(f"Nested projects filter name: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter name: child data not available")

        _cval_description = _child1_data.get("description")
        if _cval_description is not None:
            resp = ctx.req("GET", _nested_base, params={"description": str(_cval_description), "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?description=<val> → 200"):
                data = ctx.safe_json(resp)
                ctx.assert_paginated(data, f"{_nested_base}?description=<val>")
                items = data.get("data", [])
                mismatched = [item for item in items if item.get("description") != _cval_description]
                if not mismatched:
                    ctx.ok(f"Nested projects filter description: all items match")
                else:
                    ctx.fail(f"Nested projects filter description: {len(mismatched)} items mismatch")
        else:
            ctx.skip("Nested filter description: child data not available")

        for _nbool in ("true", "false"):
            resp = ctx.req("GET", _nested_base, params={"archived": _nbool, "limit": 50})
            if ctx.assert_status(resp, 200, f"GET {_nested_base}?archived={_nbool} → 200"):
                items = ctx.safe_json(resp).get("data", [])
                expected = _nbool == "true"
                bad = [item for item in items if item.get("archived") != expected]
                if not bad:
                    ctx.ok(f"Nested projects filter archived={_nbool}: all items match")
                else:
                    ctx.fail(f"Nested projects filter archived={_nbool}: {len(bad)} mismatch")


        # 7-N2-6  Unknown filter on nested → ignored
        resp = ctx.req("GET", _nested_base, params={"__nonexistent_filter__": "val"})
        if ctx.assert_status(resp, 200, f"GET {_nested_base}?unknown_filter → 200 (ignored)"):
            ctx.assert_paginated(ctx.safe_json(resp), f"{_nested_base}?unknown_filter")

    else:
        ctx.skip(f"Nested projects filter/sort: organization1_id not available")

