#!/usr/bin/env python3
"""Validate an interview-the-system evidence package using only the standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"draft", "pending human review"}
SOURCE_KINDS = {"current", "proposed", "derived", "external"}
CLAIM_CLASSES = {"fact", "inference", "decision", "question"}
RELATIONSHIP_STATUSES = {"evidenced", "inferred", "unresolved"}
REQUIRED_BRIEF_HEADINGS = (
    "# Technical Brief",
    "## Status",
    "## Question and Outcome",
    "## Scope and Authority",
    "## Evidence Consulted",
    "## Findings",
    "## Ontology",
    "## Decisions and Open Questions",
    "## Risks and Stop Conditions",
    "## Human Review",
)
TRACE_FIELDS = {
    "timestamp",
    "run_id",
    "phase",
    "action",
    "target",
    "outcome",
    "evidence_references",
}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _owner_is_valid(value: Any) -> bool:
    return _is_nonempty_string(value) and value.strip().lower() not in {"tbd", "unknown", "none"}


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}")
    return None


def _require_keys(value: Any, keys: set[str], location: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{location} must be an object")
        return
    for key in sorted(keys - value.keys()):
        errors.append(f"{location} missing required field: {key}")


def _validate_authority(authority: Any, errors: list[str]) -> None:
    required = {"read_only", "allowed_tools", "prohibited_actions", "stop_conditions"}
    _require_keys(authority, required, "authority", errors)
    if not isinstance(authority, dict):
        return
    if not isinstance(authority.get("read_only"), bool):
        errors.append("authority.read_only must be a boolean")
    for field in ("allowed_tools", "prohibited_actions", "stop_conditions"):
        if not _is_nonempty_list(authority.get(field)):
            errors.append(f"authority.{field} must be a non-empty list")


def _validate_context_sources(sources: Any, errors: list[str]) -> set[str]:
    if not _is_nonempty_list(sources):
        errors.append("context_sources must be a non-empty list")
        return set()
    source_ids: set[str] = set()
    required = {"id", "kind", "location", "purpose", "freshness", "authority"}
    for index, source in enumerate(sources):
        location = f"context_sources[{index}]"
        _require_keys(source, required, location, errors)
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        if not _is_nonempty_string(source_id):
            errors.append(f"{location}.id must be a non-empty string")
        elif source_id in source_ids:
            errors.append(f"duplicate context source id: {source_id}")
        else:
            source_ids.add(source_id)
        if source.get("kind") not in SOURCE_KINDS:
            errors.append(f"{location}.kind must be one of {sorted(SOURCE_KINDS)}")
        for field in ("location", "purpose", "freshness", "authority"):
            if not _is_nonempty_string(source.get(field)):
                errors.append(f"{location}.{field} must be a non-empty string")
    return source_ids


def _validate_claims(claims: Any, source_ids: set[str], errors: list[str]) -> set[str]:
    if not _is_nonempty_list(claims):
        errors.append("claims must be a non-empty list")
        return set()
    claim_ids: set[str] = set()
    required = {"id", "statement", "classification", "evidence_references"}
    for index, claim in enumerate(claims):
        location = f"claims[{index}]"
        _require_keys(claim, required, location, errors)
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("id")
        if not _is_nonempty_string(claim_id):
            errors.append(f"{location}.id must be a non-empty string")
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        else:
            claim_ids.add(claim_id)
        if not _is_nonempty_string(claim.get("statement")):
            errors.append(f"{location}.statement must be a non-empty string")
        classification = claim.get("classification")
        if classification not in CLAIM_CLASSES:
            errors.append(f"{location}.classification must be one of {sorted(CLAIM_CLASSES)}")
        references = claim.get("evidence_references")
        if not isinstance(references, list):
            errors.append(f"{location}.evidence_references must be a list")
            references = []
        if classification in {"fact", "inference"} and not references:
            errors.append(f"{location} {classification} requires evidence_references")
        for reference in references:
            if reference not in source_ids and reference not in claim_ids:
                errors.append(f"{location} references unknown evidence: {reference}")
        if classification == "inference" and not _is_nonempty_string(claim.get("reasoning")):
            errors.append(f"{location} inference requires reasoning")
        if classification == "decision" and not _owner_is_valid(claim.get("owner")):
            errors.append(f"{location} decision requires a named owner")
        if classification == "question":
            if not _owner_is_valid(claim.get("owner")):
                errors.append(f"{location} question requires a named owner")
            if not _is_nonempty_string(claim.get("next_action")):
                errors.append(f"{location} question requires next_action")
    return claim_ids


def _validate_ontology(ontology: Any, evidence_ids: set[str], errors: list[str]) -> None:
    required = {"entities", "concepts", "events", "relationships", "rules"}
    _require_keys(ontology, required, "ontology", errors)
    if not isinstance(ontology, dict):
        return
    node_names: set[str] = set()
    for collection_name in ("entities", "concepts", "events", "rules"):
        collection = ontology.get(collection_name)
        if not isinstance(collection, list):
            errors.append(f"ontology.{collection_name} must be a list")
            continue
        for index, item in enumerate(collection):
            location = f"ontology.{collection_name}[{index}]"
            if not isinstance(item, dict) or not _is_nonempty_string(item.get("name")):
                errors.append(f"{location}.name must be a non-empty string")
                continue
            name = item["name"]
            if name in node_names:
                errors.append(f"duplicate ontology node name: {name}")
            node_names.add(name)
            if item.get("status") == "unresolved":
                if not _owner_is_valid(item.get("owner")):
                    errors.append(f"{location} unresolved node requires a named owner")
                if not _is_nonempty_list(item.get("questions")):
                    errors.append(f"{location} unresolved node requires questions")

    relationships = ontology.get("relationships")
    if not isinstance(relationships, list):
        errors.append("ontology.relationships must be a list")
        return
    required_relationship = {"subject", "predicate", "object", "status", "evidence_references"}
    for index, relationship in enumerate(relationships):
        location = f"ontology.relationships[{index}]"
        _require_keys(relationship, required_relationship, location, errors)
        if not isinstance(relationship, dict):
            continue
        for endpoint in ("subject", "object"):
            if relationship.get(endpoint) not in node_names:
                errors.append(f"{location}.{endpoint} references unknown ontology node: {relationship.get(endpoint)}")
        if not _is_nonempty_string(relationship.get("predicate")):
            errors.append(f"{location}.predicate must be a non-empty string")
        status = relationship.get("status")
        if status not in RELATIONSHIP_STATUSES:
            errors.append(f"{location}.status must be one of {sorted(RELATIONSHIP_STATUSES)}")
        references = relationship.get("evidence_references")
        if not isinstance(references, list):
            errors.append(f"{location}.evidence_references must be a list")
            references = []
        for reference in references:
            if reference not in evidence_ids:
                errors.append(f"{location} references unknown evidence: {reference}")
        if status in {"evidenced", "inferred"} and not references:
            errors.append(f"{location} {status} relationship requires evidence_references")
        if status == "unresolved":
            if not _owner_is_valid(relationship.get("owner")):
                errors.append(f"{location} unresolved relationship requires a named owner")
            if not _is_nonempty_list(relationship.get("questions")):
                errors.append(f"{location} unresolved relationship requires questions")


def _validate_open_questions(questions: Any, errors: list[str]) -> None:
    if not isinstance(questions, list):
        errors.append("open_questions must be a list")
        return
    for index, question in enumerate(questions):
        location = f"open_questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{location} must be an object")
            continue
        if not _is_nonempty_string(question.get("question")):
            errors.append(f"{location}.question must be a non-empty string")
        if not _owner_is_valid(question.get("owner")):
            errors.append(f"{location}.owner must name an owner")
        if not _is_nonempty_string(question.get("next_action")):
            errors.append(f"{location}.next_action must be a non-empty string")


def validate_investigation(path: Path) -> list[str]:
    errors: list[str] = []
    package = _load_json(path, errors)
    if not isinstance(package, dict):
        if package is not None:
            errors.append("investigation.json root must be an object")
        return errors

    required = {
        "schema_version",
        "status",
        "question",
        "outcome",
        "scope",
        "authority",
        "context_sources",
        "claims",
        "ontology",
        "open_questions",
    }
    _require_keys(package, required, "investigation", errors)
    if package.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if package.get("status") not in VALID_STATUSES:
        errors.append(f"status must be one of {sorted(VALID_STATUSES)}")
    for field in ("question", "outcome"):
        if not _is_nonempty_string(package.get(field)):
            errors.append(f"{field} must be a non-empty string")
    scope = package.get("scope")
    _require_keys(scope, {"in", "out"}, "scope", errors)
    if isinstance(scope, dict):
        for field in ("in", "out"):
            if not isinstance(scope.get(field), list):
                errors.append(f"scope.{field} must be a list")

    _validate_authority(package.get("authority"), errors)
    source_ids = _validate_context_sources(package.get("context_sources"), errors)
    claim_ids = _validate_claims(package.get("claims"), source_ids, errors)
    _validate_ontology(package.get("ontology"), source_ids | claim_ids, errors)
    _validate_open_questions(package.get("open_questions"), errors)
    return errors


def validate_brief(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing file: {path}"]
    errors = [f"technical brief missing heading: {heading}" for heading in REQUIRED_BRIEF_HEADINGS if heading not in content]
    status_match = re.search(r"^## Status\s*$\n+([^\n]+)", content, flags=re.MULTILINE)
    if not status_match or status_match.group(1).strip().lower() not in VALID_STATUSES:
        errors.append("technical brief status must be draft or pending human review")
    return errors


def validate_trace(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return [f"missing file: {path}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"trace line {line_number} is not valid JSON")
            continue
        if not isinstance(event, dict):
            errors.append(f"trace line {line_number} must be an object")
            continue
        missing = TRACE_FIELDS - event.keys()
        if missing:
            errors.append(f"trace line {line_number} missing fields: {', '.join(sorted(missing))}")
        if not isinstance(event.get("evidence_references"), list):
            errors.append(f"trace line {line_number} evidence_references must be a list")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) not in {3, 4}:
        print("usage: validate_investigation.py investigation.json technical-brief.md [trace.jsonl]")
        print("CHECK_INVESTIGATION=USAGE_ERROR")
        return 2

    errors = validate_investigation(Path(argv[1]))
    errors.extend(validate_brief(Path(argv[2])))
    if len(argv) == 4:
        errors.extend(validate_trace(Path(argv[3])))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("CHECK_INVESTIGATION=FAIL")
        return 1

    print("Investigation package is structurally valid; semantic human review is still required.")
    print("CHECK_INVESTIGATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
