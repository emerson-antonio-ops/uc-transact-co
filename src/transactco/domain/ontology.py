"""Load and query the small, evidence-aware TransactCo ontology."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_ONTOLOGY_PATH = Path(__file__).with_name("transactco.ontology.json")
VALID_STATUSES = {"evidenced", "inferred", "unresolved"}


class OntologyError(ValueError):
    """Raised when an ontology cannot be loaded or queried safely."""


def load_ontology(path: str | Path | None = None) -> dict[str, Any]:
    """Load an ontology and reject structurally invalid content."""
    ontology_path = Path(path) if path is not None else DEFAULT_ONTOLOGY_PATH
    try:
        data = json.loads(ontology_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OntologyError(f"ontology file not found: {ontology_path}") from exc
    except json.JSONDecodeError as exc:
        raise OntologyError(
            f"invalid ontology JSON at line {exc.lineno}, column {exc.colno}: {ontology_path}"
        ) from exc
    if not isinstance(data, dict):
        raise OntologyError("ontology root must be an object")
    errors = validate_ontology(data)
    if errors:
        raise OntologyError("invalid ontology:\n- " + "\n- ".join(errors))
    return data


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_owner(value: Any) -> bool:
    return _is_nonempty_string(value) and value.strip().lower() not in {"tbd", "unknown", "none"}


def validate_ontology(data: Any) -> list[str]:
    """Return deterministic structural errors without claiming semantic correctness."""
    if not isinstance(data, dict):
        return ["ontology root must be an object"]

    errors: list[str] = []
    required_top_level = {
        "name",
        "version",
        "status",
        "evidence_sources",
        "entities",
        "concepts",
        "events",
        "relationships",
        "rules",
    }
    for field in sorted(required_top_level - data.keys()):
        errors.append(f"missing top-level field: {field}")
    for field in ("name", "version", "status"):
        if not _is_nonempty_string(data.get(field)):
            errors.append(f"{field} must be a non-empty string")

    sources = data.get("evidence_sources")
    source_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errors.append("evidence_sources must be a non-empty list")
    else:
        for index, source in enumerate(sources):
            location = f"evidence_sources[{index}]"
            if not isinstance(source, dict):
                errors.append(f"{location} must be an object")
                continue
            for field in ("id", "location", "authority"):
                if not _is_nonempty_string(source.get(field)):
                    errors.append(f"{location}.{field} must be a non-empty string")
            source_id = source.get("id")
            if _is_nonempty_string(source_id):
                if source_id in source_ids:
                    errors.append(f"duplicate evidence source id: {source_id}")
                source_ids.add(source_id)

    nodes: dict[str, str] = {}
    for collection_name in ("entities", "concepts", "events", "rules"):
        collection = data.get(collection_name)
        if not isinstance(collection, list):
            errors.append(f"{collection_name} must be a list")
            continue
        for index, item in enumerate(collection):
            location = f"{collection_name}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{location} must be an object")
                continue
            name = item.get("name")
            if not _is_nonempty_string(name):
                errors.append(f"{location}.name must be a non-empty string")
                continue
            if name in nodes:
                errors.append(f"duplicate ontology node name: {name}")
            nodes[name] = collection_name
            status = item.get("status")
            if status not in VALID_STATUSES:
                errors.append(f"{location}.status must be one of {sorted(VALID_STATUSES)}")
            references = item.get("evidence_references", [])
            if not isinstance(references, list):
                errors.append(f"{location}.evidence_references must be a list")
            else:
                for reference in references:
                    if reference not in source_ids:
                        errors.append(f"{location} references unknown evidence source: {reference}")
            if status == "unresolved":
                if not _has_owner(item.get("owner")):
                    errors.append(f"{location} unresolved node requires a named owner")
                if not isinstance(item.get("questions"), list) or not item["questions"]:
                    errors.append(f"{location} unresolved node requires questions")

    relationship_nodes = {
        name for name, collection_name in nodes.items() if collection_name in {"entities", "concepts"}
    }
    relationships = data.get("relationships")
    if not isinstance(relationships, list):
        errors.append("relationships must be a list")
    else:
        for index, relationship in enumerate(relationships):
            location = f"relationships[{index}]"
            if not isinstance(relationship, dict):
                errors.append(f"{location} must be an object")
                continue
            for field in ("subject", "predicate", "object"):
                if not _is_nonempty_string(relationship.get(field)):
                    errors.append(f"{location}.{field} must be a non-empty string")
            for endpoint in ("subject", "object"):
                value = relationship.get(endpoint)
                if _is_nonempty_string(value) and value not in relationship_nodes:
                    errors.append(f"{location}.{endpoint} references unknown entity or concept: {value}")
            status = relationship.get("status")
            if status not in VALID_STATUSES:
                errors.append(f"{location}.status must be one of {sorted(VALID_STATUSES)}")
            references = relationship.get("evidence_references")
            if not isinstance(references, list):
                errors.append(f"{location}.evidence_references must be a list")
                references = []
            for reference in references:
                if reference not in source_ids:
                    errors.append(f"{location} references unknown evidence source: {reference}")
            if status in {"evidenced", "inferred"} and not references:
                errors.append(f"{location} {status} relationship requires evidence")
            if status == "unresolved":
                if not _has_owner(relationship.get("owner")):
                    errors.append(f"{location} unresolved relationship requires a named owner")
                if not isinstance(relationship.get("questions"), list) or not relationship["questions"]:
                    errors.append(f"{location} unresolved relationship requires questions")

    return errors


def list_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return entity and concept summaries for a compact CLI view."""
    rows: list[dict[str, Any]] = []
    for node_type, collection_name in (("entity", "entities"), ("concept", "concepts")):
        for node in data[collection_name]:
            rows.append(
                {
                    "type": node_type,
                    "name": node["name"],
                    "status": node["status"],
                    "source": node.get("source", ", ".join(node.get("candidate_inputs", []))),
                    "owner": node.get("owner", "—"),
                }
            )
    return rows


def explain_concept(data: dict[str, Any], name: str) -> dict[str, Any]:
    """Explain a concept and surface, rather than invent, missing decisions."""
    normalized = name.casefold()
    concept = next(
        (item for item in data["concepts"] if item["name"].casefold() == normalized),
        None,
    )
    if concept is None:
        available = ", ".join(item["name"] for item in data["concepts"])
        raise OntologyError(f"unknown concept: {name}. Available concepts: {available}")

    relationships = [
        relationship
        for relationship in data["relationships"]
        if relationship["subject"] == concept["name"] or relationship["object"] == concept["name"]
    ]
    required_decisions: list[dict[str, str]] = []
    for question in concept.get("questions", []):
        if isinstance(question, dict):
            required_decisions.append(
                {"question": question["question"], "owner": question.get("owner", concept.get("owner", "—"))}
            )
        else:
            required_decisions.append({"question": str(question), "owner": concept.get("owner", "—")})
    for relationship in relationships:
        if relationship.get("status") != "unresolved":
            continue
        for question in relationship.get("questions", []):
            candidate = {"question": str(question), "owner": relationship.get("owner", "—")}
            if candidate not in required_decisions:
                required_decisions.append(candidate)

    blocked = concept.get("status") == "unresolved" or any(
        relationship.get("status") == "unresolved" for relationship in relationships
    )
    answerability = (
        "blocked_by_business_decisions"
        if blocked
        else "candidate_semantics"
        if concept.get("status") == "inferred"
        else "answerable_from_declared_semantics"
    )
    return {
        "name": concept["name"],
        "status": concept["status"],
        "answerability": answerability,
        "description": concept.get("description", ""),
        "owner": concept.get("owner", "—"),
        "candidate_inputs": concept.get("candidate_inputs", []),
        "relationships": relationships,
        "required_decisions": required_decisions,
        "evidence_references": concept.get("evidence_references", []),
    }
