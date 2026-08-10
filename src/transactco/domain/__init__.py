"""TransactCo entities, relationships, invariants, and shared business meaning."""

from .ontology import (
    DEFAULT_ONTOLOGY_PATH,
    OntologyError,
    explain_concept,
    list_nodes,
    load_ontology,
    validate_ontology,
)

__all__ = [
    "DEFAULT_ONTOLOGY_PATH",
    "OntologyError",
    "explain_concept",
    "list_nodes",
    "load_ontology",
    "validate_ontology",
]
