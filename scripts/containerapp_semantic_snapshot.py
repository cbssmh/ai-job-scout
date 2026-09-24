#!/usr/bin/env python3
"""Build a deterministic, secret-safe Container App semantic snapshot."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


TARGET_IMAGE_SENTINEL = "<TARGET_IMAGE_CHANGE_ALLOWED>"
SENSITIVE_KEYS = {
    "clientsecret",
    "connectionstring",
    "password",
    "secret",
    "secretvalue",
    "token",
    "value",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _fingerprint(value: Any, hmac_key: bytes) -> str:
    return hmac.new(hmac_key, _canonical(value), hashlib.sha256).hexdigest()


def _fingerprinted(value: Any, hmac_key: bytes) -> dict[str, Any]:
    if value is None:
        return {"configured": False, "fingerprint": None}
    return {
        "configured": True,
        "fingerprint": _fingerprint(value, hmac_key),
    }


def _sanitize(value: Any, hmac_key: bytes) -> Any:
    if isinstance(value, list):
        return [_sanitize(item, hmac_key) for item in value]
    if not isinstance(value, dict):
        return value

    sanitized: dict[str, Any] = {}
    for key in sorted(value):
        item = value[key]
        if key.lower() in SENSITIVE_KEYS:
            sanitized[f"{key}Protection"] = _fingerprinted(item, hmac_key)
        else:
            sanitized[key] = _sanitize(item, hmac_key)
    return sanitized


def _sort_objects(values: list[Any]) -> list[Any]:
    return sorted(values, key=_canonical)


def _snapshot_environment(
    environment: list[dict[str, Any]] | None,
    hmac_key: bytes,
) -> list[dict[str, Any]]:
    result = []
    for item in environment or []:
        has_value = "value" in item and item["value"] is not None
        result.append(
            {
                "name": item.get("name"),
                "secretRef": item.get("secretRef"),
                "literalValue": (
                    _fingerprinted(item["value"], hmac_key)
                    if has_value
                    else {"configured": False, "fingerprint": None}
                ),
            }
        )
    return sorted(
        result,
        key=lambda item: (
            item.get("name") or "",
            item.get("secretRef") or "",
        ),
    )


def _snapshot_container(
    container: dict[str, Any],
    target_container: str,
    hmac_key: bytes,
) -> dict[str, Any]:
    name = container.get("name")
    probes = [_sanitize(probe, hmac_key) for probe in container.get("probes") or []]
    mounts = [
        _sanitize(mount, hmac_key)
        for mount in container.get("volumeMounts") or []
    ]
    return {
        "name": name,
        "image": (
            TARGET_IMAGE_SENTINEL
            if name == target_container
            else container.get("image")
        ),
        "resources": _sanitize(container.get("resources"), hmac_key),
        "environment": _snapshot_environment(container.get("env"), hmac_key),
        "probes": _sort_objects(probes),
        "volumeMounts": _sort_objects(mounts),
        "command": _fingerprinted(container.get("command"), hmac_key),
        "args": _fingerprinted(container.get("args"), hmac_key),
        "identity": _sanitize(container.get("identity"), hmac_key),
        "securityContext": _sanitize(
            container.get("securityContext"),
            hmac_key,
        ),
    }


def _snapshot_ingress(ingress: dict[str, Any] | None, hmac_key: bytes) -> Any:
    if ingress is None:
        return None
    result = dict(ingress)
    traffic = []
    for rule in result.get("traffic") or []:
        sanitized_rule = dict(rule)
        sanitized_rule.pop("revisionName", None)
        traffic.append(_sanitize(sanitized_rule, hmac_key))
    result["traffic"] = _sort_objects(traffic)
    return _sanitize(result, hmac_key)


def _snapshot_registries(
    registries: list[dict[str, Any]] | None,
    hmac_key: bytes,
) -> list[dict[str, Any]]:
    result = []
    for registry in registries or []:
        result.append(
            {
                "server": registry.get("server"),
                "identity": registry.get("identity"),
                "passwordSecretRef": registry.get("passwordSecretRef"),
                "username": _fingerprinted(registry.get("username"), hmac_key),
            }
        )
    return sorted(result, key=lambda item: item.get("server") or "")


def build_snapshot(
    app: dict[str, Any],
    target_container: str,
    hmac_key: bytes,
) -> dict[str, Any]:
    properties = app.get("properties") or {}
    configuration = properties.get("configuration") or {}
    template = properties.get("template") or {}
    identity = app.get("identity") or {}

    containers = [
        _snapshot_container(container, target_container, hmac_key)
        for container in template.get("containers") or []
    ]
    init_containers = [
        _snapshot_container(container, "", hmac_key)
        for container in template.get("initContainers") or []
    ]

    return {
        "workloadIdentity": {
            "type": identity.get("type"),
            "userAssignedIdentityIds": sorted(
                (identity.get("userAssignedIdentities") or {}).keys()
            ),
            "identitySettings": _sort_objects(
                [
                    _sanitize(setting, hmac_key)
                    for setting in configuration.get("identitySettings") or []
                ]
            ),
        },
        "environmentId": (
            properties.get("environmentId")
            or properties.get("managedEnvironmentId")
        ),
        "workloadProfileName": properties.get("workloadProfileName"),
        "configuration": {
            "activeRevisionsMode": configuration.get("activeRevisionsMode"),
            "ingress": _snapshot_ingress(configuration.get("ingress"), hmac_key),
            "registries": _snapshot_registries(
                configuration.get("registries"),
                hmac_key,
            ),
            "secretNames": sorted(
                secret.get("name")
                for secret in configuration.get("secrets") or []
                if secret.get("name") is not None
            ),
            "dapr": _sanitize(configuration.get("dapr"), hmac_key),
            "runtime": _sanitize(configuration.get("runtime"), hmac_key),
            "service": _sanitize(configuration.get("service"), hmac_key),
            "maxInactiveRevisions": configuration.get("maxInactiveRevisions"),
        },
        "template": {
            "scale": {
                "minReplicas": (template.get("scale") or {}).get("minReplicas"),
                "maxReplicas": (template.get("scale") or {}).get("maxReplicas"),
                "cooldownPeriod": (template.get("scale") or {}).get(
                    "cooldownPeriod"
                ),
                "pollingInterval": (template.get("scale") or {}).get(
                    "pollingInterval"
                ),
                "rules": _sort_objects(
                    [
                        _sanitize(rule, hmac_key)
                        for rule in (template.get("scale") or {}).get("rules") or []
                    ]
                ),
            },
            "containers": sorted(containers, key=lambda item: item.get("name") or ""),
            "initContainers": sorted(
                init_containers,
                key=lambda item: item.get("name") or "",
            ),
            "volumes": _sort_objects(
                [
                    _sanitize(volume, hmac_key)
                    for volume in template.get("volumes") or []
                ]
            ),
            "serviceBinds": _sort_objects(
                [
                    _sanitize(binding, hmac_key)
                    for binding in template.get("serviceBinds") or []
                ]
            ),
            "terminationGracePeriodSeconds": template.get(
                "terminationGracePeriodSeconds"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--target-container", required=True)
    parser.add_argument("--hmac-key-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    app = json.loads(args.input.read_text(encoding="utf-8"))
    hmac_key = args.hmac_key_file.read_bytes().strip()
    if not hmac_key:
        raise SystemExit("semantic snapshot HMAC key is empty")

    snapshot = build_snapshot(app, args.target_container, hmac_key)
    args.output.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
