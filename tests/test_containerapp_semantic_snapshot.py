import copy
import json
from pathlib import Path

from scripts.containerapp_semantic_snapshot import (
    TARGET_IMAGE_SENTINEL,
    build_snapshot,
)


FIXTURES = (
    Path(__file__).parent / "fixtures" / "containerapp_semantic_states.json"
)
HMAC_KEY = b"deterministic-test-only-hmac-key"
TARGET_CONTAINER = "api"


def _fixtures():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _snapshot(state):
    return build_snapshot(state, TARGET_CONTAINER, HMAC_KEY)


def _state_for(case_name):
    fixtures = _fixtures()
    state = copy.deepcopy(fixtures["before"])
    case = fixtures["cases"][case_name]
    properties = state["properties"]
    template = properties["template"]
    target = next(
        container
        for container in template["containers"]
        if container["name"] == TARGET_CONTAINER
    )
    target["image"] = case["targetImage"]

    if "maxReplicas" in case:
        template["scale"]["maxReplicas"] = case["maxReplicas"]

    if "principalId" in case:
        state["identity"]["principalId"] = case["principalId"]
        properties["latestRevisionName"] = case["revisionName"]
        properties["latestReadyRevisionName"] = case["revisionName"]
        properties["runningStatus"] = "Running"
        template["revisionSuffix"] = case["revisionName"].rsplit("--", 1)[-1]
        properties["configuration"]["ingress"]["traffic"][0][
            "revisionName"
        ] = case["revisionName"]

    if case.get("normalizeEmptyArrays"):
        template["initContainers"] = None
        template["volumes"] = []
        template["serviceBinds"] = []

    if case.get("reverseUnorderedArrays"):
        template["containers"].reverse()
        target["env"].reverse()
        target["probes"].reverse()

    return state


def test_benign_azure_normalization_does_not_fail():
    fixtures = _fixtures()

    assert _snapshot(fixtures["before"]) == _snapshot(
        _state_for("benignNormalization")
    )


def test_protected_field_change_fails_comparison():
    fixtures = _fixtures()

    before = _snapshot(fixtures["before"])
    drifted = _snapshot(_state_for("protectedDrift"))

    assert before != drifted
    assert before["template"]["scale"]["maxReplicas"] == 1
    assert drifted["template"]["scale"]["maxReplicas"] == 2


def test_target_image_only_change_passes():
    fixtures = _fixtures()

    before = _snapshot(fixtures["before"])
    image_only = _snapshot(_state_for("imageOnly"))

    assert before == image_only
    target = next(
        container
        for container in image_only["template"]["containers"]
        if container["name"] == TARGET_CONTAINER
    )
    assert target["image"] == TARGET_IMAGE_SENTINEL


def test_snapshot_covers_protected_contract_without_secret_values():
    fixtures = _fixtures()
    snapshot = _snapshot(fixtures["before"])
    serialized = json.dumps(snapshot, sort_keys=True)

    assert snapshot["configuration"]["activeRevisionsMode"] == "Single"
    assert snapshot["configuration"]["ingress"]["targetPort"] == 8000
    assert snapshot["configuration"]["registries"][0]["server"]
    assert snapshot["workloadIdentity"]["type"] == "SystemAssigned"
    assert snapshot["template"]["scale"]["minReplicas"] == 0
    assert snapshot["template"]["scale"]["maxReplicas"] == 1
    assert snapshot["template"]["scale"]["rules"]
    assert len(snapshot["template"]["containers"]) == 2
    assert "synthetic-secret-value-not-real" not in serialized
    assert "synthetic-literal-value-not-real" not in serialized
    assert "synthetic-registry-user" not in serialized
