"""
Section 30 — Cleanup: delete all test data created during the suite.

Order: child entities first (reverse dependency order).
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("30 · CLEANUP — Remove test data")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")

    def _delete(path: str, token: str | None, label: str) -> None:
        if not token:
            ctx.warn(f"Cleanup: no token for {label}, skipping")
            return
        resp = ctx.req("DELETE", path, token=token)
        if resp.status_code == 403:
            # First token didn't own this resource; try the other user's token
            fallback = token2 if token is token1 else token1
            if fallback:
                resp = ctx.req("DELETE", path, token=fallback)
        if resp.status_code in (204, 404):
            ctx.ok(f"Cleanup: {label} removed (HTTP {resp.status_code})")
        elif resp.status_code == 403:
            ctx.warn(f"Cleanup: {label} → 403 Forbidden (neither token owns this resource)")
        else:
            ctx.warn(f"Cleanup: {label} → unexpected HTTP {resp.status_code}")

    # Cleanup taskComments
    taskComment_cleanups = [
        (ctx.state.get("taskComment1_id"), token1, "taskComment1_id"),
        (ctx.state.get("taskComment2_id"), token1, "taskComment2_id"),
        (ctx.state.get("taskComment3_id"), token1, "taskComment3_id"),
        (ctx.state.get("spoofed_taskComment_id"), token1, "spoofed_taskComment_id"),
        (ctx.state.get("long_title_taskComment_id"), token1, "long_title_taskComment_id"),
        (ctx.state.get("long_content_taskComment_id"), token1, "long_content_taskComment_id"),
        (ctx.state.get("xss_taskComment_id"), token1, "xss_taskComment_id"),
        (ctx.state.get("unicode_taskComment_id"), token1, "unicode_taskComment_id"),
    ]
    for eid, tok, label in taskComment_cleanups:
        if eid:
            _delete("/api/taskComments/" + str(eid), tok, label)

    # Cleanup tasks
    task_cleanups = [
        (ctx.state.get("task1_id"), token1, "task1_id"),
        (ctx.state.get("task2_id"), token1, "task2_id"),
        (ctx.state.get("task3_id"), token1, "task3_id"),
        (ctx.state.get("spoofed_task_id"), token1, "spoofed_task_id"),
        (ctx.state.get("long_title_task_id"), token1, "long_title_task_id"),
        (ctx.state.get("long_content_task_id"), token1, "long_content_task_id"),
        (ctx.state.get("xss_task_id"), token1, "xss_task_id"),
        (ctx.state.get("unicode_task_id"), token1, "unicode_task_id"),
    ]
    for eid, tok, label in task_cleanups:
        if eid:
            _delete("/api/tasks/" + str(eid), tok, label)

    # Cleanup projects
    project_cleanups = [
        (ctx.state.get("project1_id"), token1, "project1_id"),
        (ctx.state.get("project2_id"), token1, "project2_id"),
        (ctx.state.get("project3_id"), token1, "project3_id"),
        (ctx.state.get("spoofed_project_id"), token1, "spoofed_project_id"),
        (ctx.state.get("long_title_project_id"), token1, "long_title_project_id"),
        (ctx.state.get("long_content_project_id"), token1, "long_content_project_id"),
        (ctx.state.get("xss_project_id"), token1, "xss_project_id"),
        (ctx.state.get("unicode_project_id"), token1, "unicode_project_id"),
    ]
    for eid, tok, label in project_cleanups:
        if eid:
            _delete("/api/projects/" + str(eid), tok, label)

    # Cleanup memberships
    membership_cleanups = [
        (ctx.state.get("membership1_id"), token1, "membership1_id"),
        (ctx.state.get("membership2_id"), token1, "membership2_id"),
        (ctx.state.get("membership3_id"), token1, "membership3_id"),
        (ctx.state.get("spoofed_membership_id"), token1, "spoofed_membership_id"),
        (ctx.state.get("long_title_membership_id"), token1, "long_title_membership_id"),
        (ctx.state.get("long_content_membership_id"), token1, "long_content_membership_id"),
        (ctx.state.get("xss_membership_id"), token1, "xss_membership_id"),
        (ctx.state.get("unicode_membership_id"), token1, "unicode_membership_id"),
    ]
    for eid, tok, label in membership_cleanups:
        if eid:
            _delete("/api/memberships/" + str(eid), tok, label)

    # Cleanup organizations
    organization_cleanups = [
        (ctx.state.get("organization1_id"), token1, "organization1_id"),
        (ctx.state.get("organization2_id"), token1, "organization2_id"),
        (ctx.state.get("organization3_id"), token1, "organization3_id"),
        (ctx.state.get("spoofed_organization_id"), token1, "spoofed_organization_id"),
        (ctx.state.get("long_title_organization_id"), token1, "long_title_organization_id"),
        (ctx.state.get("long_content_organization_id"), token1, "long_content_organization_id"),
        (ctx.state.get("xss_organization_id"), token1, "xss_organization_id"),
        (ctx.state.get("unicode_organization_id"), token1, "unicode_organization_id"),
    ]
    for eid, tok, label in organization_cleanups:
        if eid:
            _delete("/api/organizations/" + str(eid), tok, label)

