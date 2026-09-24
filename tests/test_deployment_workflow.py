from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "deploy.yml"


def _image_patch_step() -> str:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    start = workflow.index("      - name: Submit minimal image-only Container App patch")
    end = workflow.index("\n      - name:", start + 1)
    return workflow[start:end]


def _revision_wait_step() -> str:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    start = workflow.index("      - name: Wait for and verify the new revision")
    end = workflow.index("\n      - name:", start + 1)
    return workflow[start:end]


def test_container_app_patch_uses_documented_media_type_and_existing_location():
    step = _image_patch_step()

    assert "--headers 'Content-Type=application/json'" in step
    assert "application/merge-patch+json" not in step
    assert 'location="$(jq -r \'.location // empty\' "$app_before")"' in step
    assert '--arg location "$location"' in step
    assert "location: $location" in step
    assert '(keys == ["location", "properties"])' in step
    assert "and (.location == $location)" in step


def test_container_app_patch_remains_narrow_and_polls_after_acceptance():
    step = _image_patch_step()
    wait_step = _revision_wait_step()

    assert '(keys == ["location", "properties"])' in step
    assert 'and (.properties | keys == ["template"])' in step
    assert 'and (.properties.template | keys == ["containers"])' in step
    assert "HTTP 200 or 202" in step
    assert "for attempt in {1..60}" in wait_step
    assert 'az rest --method get --url "$app_url"' in wait_step
    assert 'az rest --method get --url "$revision_url"' in wait_step
    assert "operation-status" not in (step + wait_step)
    assert "azure-asyncoperation" not in (step + wait_step).lower()


def test_semantic_gate_uses_sanitized_allowlist_snapshots():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert workflow.count("scripts/containerapp_semantic_snapshot.py") == 2
    assert '"$RUNNER_TEMP/semantic-before.json"' in workflow
    assert '"$RUNNER_TEMP/semantic-after.json"' in workflow
    assert 'cat "$semantic_before"' in workflow
    assert 'cat "$semantic_after"' in workflow
    assert 'diff --unified "$semantic_before" "$semantic_after"' in workflow
    assert "invariant-before.json" not in workflow
    assert "invariant-after.json" not in workflow
