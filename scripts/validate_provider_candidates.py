"""Read-only provider/model contract benchmark for AI Job Scout.

The benchmark uses synthetic job postings, reads an existing credential from
``.env``, and writes metrics only. Provider response bodies are never written
to disk or printed. It does not call AI Job Scout, its database, Azure, or Key
Vault. Live provider calls require an explicit acknowledgement flag and may
consume quota or incur cost.

Example:
    .venv/bin/python scripts/validate_provider_candidates.py \
        --provider nvidia \
        --models ibm/granite-3.0-3b-a800m-instruct google/gemma-3-4b-it \
        --trials 3 \
        --acknowledge-live-provider-calls \
        --output /tmp/provider-selection-results.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from openai import APITimeoutError, OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.job_analyst import SYSTEM_PROMPT, _clean_json_text


REQUIRED_FIELDS = (
    "role",
    "tech_stack",
    "experience_level",
    "language_requirement",
    "visa_sponsorship",
    "summary",
)

STRUCTURED_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "job_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                field: {"type": "string"} for field in REQUIRED_FIELDS
            },
            "required": list(REQUIRED_FIELDS),
            "additionalProperties": False,
        },
    },
}

SYNTHETIC_POSTINGS = {
    "clear_backend": {
        "title": "Senior Backend Engineer",
        "description": (
            "Build Python and FastAPI services backed by PostgreSQL and Redis. "
            "Operate Docker workloads on Kubernetes in AWS. Requires 5+ years "
            "of backend experience and professional English. Visa sponsorship "
            "is available for qualified candidates."
        ),
    },
    "ambiguous_platform_cloud": {
        "title": "Platform Builder",
        "description": (
            "Join a small team improving how product engineers ship and observe "
            "services. Work spans cloud foundations, CI/CD, developer tooling, "
            "incident learning, and occasional application code. Experience with "
            "Terraform, Kubernetes, Go or Python is useful. Seniority, language, "
            "and immigration support are not specified."
        ),
    },
    "security_oriented": {
        "title": "Product Security Engineer",
        "description": (
            "Threat-model web services, review Python and TypeScript code, tune "
            "cloud detection controls, and help remediate vulnerabilities. Three "
            "or more years in application security is required. Fluent English "
            "is required. The company cannot sponsor work visas for this role."
        ),
    },
    "long_noisy": {
        "title": "Software Engineer, Data Platform",
        "description": (
            "ABOUT US\nWe value curiosity, kindness, ownership, inclusive teams, "
            "and sustainable delivery. Benefits may include flexible schedules, "
            "learning budgets, wellness programs, community events, and equipment.\n\n"
            "THE WORK\nDesign batch and streaming data services using Python, "
            "Scala, Spark, Airflow, Kafka, SQL, and AWS. Improve observability, "
            "data quality, deployment automation, and on-call practices. Partner "
            "with analysts, security, finance, and product teams.\n\n"
            "WHAT HELPS\nAt least 3 years building production data platforms; "
            "English communication for a distributed team. Equivalent experience "
            "is welcome. Relocation support may be considered case by case.\n\n"
            "GENERAL NOTICE\nThis synthetic posting is intentionally padded with "
            "repeated culture and process language. We are an equal opportunity "
            "employer. Applicants may request interview accommodations. Teams use "
            "quarterly planning, written proposals, demos, retrospectives, and "
            "cross-functional reviews. "
            + "Our culture statement emphasizes collaboration and learning. " * 30
        ),
    },
    "sparse": {
        "title": "Engineer",
        "description": "Help us build and maintain internal tools. Remote possible.",
    },
}


@dataclass
class TrialResult:
    model: str
    response_mode: str
    case: str
    trial: int
    latency_seconds: float
    request_completed: bool
    timeout: bool
    provider_error: bool
    http_status: int | None
    error_type: str | None
    raw_json_parse_success: bool
    app_json_parse_success: bool
    required_fields_complete: bool
    all_required_fields_strings: bool
    obvious_format_violation: bool
    degraded_fallback: bool
    contract_success: bool


def percentile_nearest_rank(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return round(ordered[rank - 1], 3)


def prompt_for(posting: dict[str, str]) -> str:
    return (
        f"\nJob title:\n{posting['title']}\n\n"
        f"Job description:\n{posting['description']}\n\nReturn JSON only.\n"
    )


def response_format_for(mode: str) -> dict[str, Any] | None:
    if mode == "json_schema":
        return STRUCTURED_SCHEMA
    if mode == "json_object":
        return {"type": "json_object"}
    return None


def make_request(
    client: OpenAI,
    model: str,
    posting: dict[str, str],
    response_mode: str,
) -> Any:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_for(posting)},
        ],
        "temperature": 0,
        "max_tokens": 800,
    }
    response_format = response_format_for(response_mode)
    if response_format is not None:
        kwargs["response_format"] = response_format
    return client.chat.completions.create(**kwargs)


def validate_content(content: str) -> dict[str, bool]:
    stripped = content.strip()
    raw_data: Any = None
    app_data: Any = None
    try:
        raw_data = json.loads(stripped)
        raw_parse = isinstance(raw_data, dict)
    except (json.JSONDecodeError, TypeError):
        raw_parse = False

    try:
        app_data = json.loads(_clean_json_text(content))
        app_parse = isinstance(app_data, dict)
    except (json.JSONDecodeError, TypeError):
        app_parse = False

    complete = bool(
        app_parse
        and all(field in app_data and app_data[field] is not None for field in REQUIRED_FIELDS)
    )
    string_fields = bool(
        complete and all(isinstance(app_data[field], str) for field in REQUIRED_FIELDS)
    )
    format_violation = bool(
        not raw_parse
        or not stripped.startswith("{")
        or not stripped.endswith("}")
        or (raw_parse and not isinstance(raw_data, dict))
    )
    app_success = bool(app_parse and complete)
    contract_success = bool(app_success and string_fields and not format_violation)
    return {
        "raw_json_parse_success": raw_parse,
        "app_json_parse_success": app_parse,
        "required_fields_complete": complete,
        "all_required_fields_strings": string_fields,
        "obvious_format_violation": format_violation,
        "degraded_fallback": not app_success,
        "contract_success": contract_success,
    }


def run_trial(
    client: OpenAI,
    model: str,
    response_mode: str,
    case_name: str,
    posting: dict[str, str],
    trial: int,
) -> TrialResult:
    started = time.perf_counter()
    try:
        response = make_request(client, model, posting, response_mode)
        latency = round(time.perf_counter() - started, 3)
        content = response.choices[0].message.content or ""
        checks = validate_content(content)
        return TrialResult(
            model=model,
            response_mode=response_mode,
            case=case_name,
            trial=trial,
            latency_seconds=latency,
            request_completed=True,
            timeout=False,
            provider_error=False,
            http_status=None,
            error_type=None,
            **checks,
        )
    except Exception as exc:  # Metrics intentionally omit provider response text.
        latency = round(time.perf_counter() - started, 3)
        timeout = isinstance(exc, APITimeoutError)
        return TrialResult(
            model=model,
            response_mode=response_mode,
            case=case_name,
            trial=trial,
            latency_seconds=latency,
            request_completed=False,
            timeout=timeout,
            provider_error=not timeout,
            http_status=getattr(exc, "status_code", None),
            error_type=type(exc).__name__,
            raw_json_parse_success=False,
            app_json_parse_success=False,
            required_fields_complete=False,
            all_required_fields_strings=False,
            obvious_format_violation=False,
            degraded_fallback=True,
            contract_success=False,
        )


def select_response_mode(client: OpenAI, model: str) -> tuple[str, list[TrialResult], bool]:
    probes: list[TrialResult] = []
    for mode in ("json_schema", "json_object", "prompt_only"):
        result = run_trial(
            client,
            model,
            mode,
            "capability_probe",
            SYNTHETIC_POSTINGS["clear_backend"],
            0,
        )
        probes.append(result)
        print(
            f"probe model={model} mode={mode} completed={result.request_completed} "
            f"contract={result.contract_success} error={result.error_type or '-'}",
            flush=True,
        )
        if result.contract_success:
            return mode, probes, True
    return "prompt_only", probes, False


def summarize(model: str, mode: str, trials: list[TrialResult]) -> dict[str, Any]:
    count = len(trials)
    completed_latencies = [x.latency_seconds for x in trials if x.request_completed]
    contract_latencies = [x.latency_seconds for x in trials if x.contract_success]

    def rate(attribute: str) -> float:
        return round(sum(bool(getattr(x, attribute)) for x in trials) / count, 4)

    errors: dict[str, int] = {}
    for trial in trials:
        if trial.error_type:
            key = f"{trial.error_type}:{trial.http_status or 'none'}"
            errors[key] = errors.get(key, 0) + 1

    return {
        "model": model,
        "response_mode": mode,
        "trial_count": count,
        "contract_success_rate": rate("contract_success"),
        "request_completion_rate": rate("request_completed"),
        "timeout_rate": rate("timeout"),
        "provider_error_rate": rate("provider_error"),
        "raw_json_parse_rate": rate("raw_json_parse_success"),
        "app_json_parse_rate": rate("app_json_parse_success"),
        "required_field_completeness_rate": rate("required_fields_complete"),
        "degraded_fallback_rate": rate("degraded_fallback"),
        "obvious_format_violation_rate": rate("obvious_format_violation"),
        "completed_latency_p50_seconds": percentile_nearest_rank(completed_latencies, 0.50),
        "completed_latency_p95_seconds": percentile_nearest_rank(completed_latencies, 0.95),
        "contract_success_latency_p50_seconds": percentile_nearest_rank(contract_latencies, 0.50),
        "contract_success_latency_p95_seconds": percentile_nearest_rank(contract_latencies, 0.95),
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("nvidia", "openai"), required=True)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--acknowledge-live-provider-calls",
        action="store_true",
        help="Required acknowledgement that the benchmark makes billable/quota-consuming calls.",
    )
    args = parser.parse_args()

    if args.trials < 2:
        raise SystemExit("--trials must be at least 2")
    if not args.acknowledge_live_provider_calls:
        raise SystemExit(
            "Refusing live provider calls without --acknowledge-live-provider-calls"
        )

    config = dotenv_values(".env")
    if args.provider == "nvidia":
        api_key = config.get("NVIDIA_API_KEY")
        base_url = config.get("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1"
    else:
        api_key = config.get("OPENAI_API_KEY")
        base_url = None
    if not api_key or api_key.startswith("your_"):
        raise SystemExit(f"No usable {args.provider} credential is locally available")

    client_kwargs: dict[str, Any] = {
        "api_key": api_key,
        "timeout": args.timeout,
        "max_retries": 0,
    }
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    all_results: list[TrialResult] = []
    capability_probes: dict[str, list[dict[str, Any]]] = {}
    summaries: list[dict[str, Any]] = []

    for model in args.models:
        mode, probes, available = select_response_mode(client, model)
        capability_probes[model] = [asdict(probe) for probe in probes]
        if not available:
            unavailable_summary = summarize(model, mode, probes)
            unavailable_summary["evaluation_scope"] = "availability_probes_only"
            unavailable_summary["available_within_timeout"] = False
            summaries.append(unavailable_summary)
            print(
                "summary " + json.dumps(unavailable_summary, sort_keys=True),
                flush=True,
            )
            continue
        model_trials: list[TrialResult] = []
        for case_name, posting in SYNTHETIC_POSTINGS.items():
            for trial_number in range(1, args.trials + 1):
                result = run_trial(
                    client,
                    model,
                    mode,
                    case_name,
                    posting,
                    trial_number,
                )
                model_trials.append(result)
                all_results.append(result)
                print(
                    f"trial model={model} case={case_name} n={trial_number} "
                    f"latency={result.latency_seconds:.3f}s "
                    f"contract={result.contract_success} fallback={result.degraded_fallback} "
                    f"error={result.error_type or '-'}",
                    flush=True,
                )
        summary = summarize(model, mode, model_trials)
        summary["evaluation_scope"] = "full_synthetic_suite"
        summary["available_within_timeout"] = True
        summaries.append(summary)
        print("summary " + json.dumps(summary, sort_keys=True), flush=True)

    artifact = {
        "generated_at": datetime.now(UTC).isoformat(),
        "provider": args.provider,
        "endpoint": "NVIDIA Public API Endpoint" if args.provider == "nvidia" else "OpenAI API",
        "timeout_seconds": args.timeout,
        "automatic_sdk_retries": 0,
        "temperature": 0,
        "max_tokens": 800,
        "synthetic_case_names": list(SYNTHETIC_POSTINGS),
        "trials_per_case": args.trials,
        "response_bodies_retained": False,
        "capability_probes": capability_probes,
        "summaries": summaries,
        "trials": [asdict(result) for result in all_results],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"wrote metrics-only artifact: {args.output}", flush=True)


if __name__ == "__main__":
    main()
