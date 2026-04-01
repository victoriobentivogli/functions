"""
rdf_entitymention_extractor.py
------------------------------
Extracts a single entity mention of a given type from an RDF string.

Nested resource references are traversed and flattened into a single-level
properties dictionary using dot-notation keys.  An optional ``property_names``
list restricts which top-level predicates (and their flattened sub-keys) are
included in the output.
"""

from __future__ import annotations

from entitymention import EntityMention
from rdflib import BNode, Graph, RDF, URIRef


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _local_name(uri: str) -> str:
    """Return the local name portion of a URI (after the last '#' or '/')."""
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.split("/")[-1]


def _merge(target: dict, key: str, value: str | list) -> None:
    """
    Merge *value* into *target[key]*, promoting to a list when there
    is already an existing value for that key.
    """
    if key not in target:
        target[key] = value
        return

    existing = target[key]
    if isinstance(existing, list):
        if isinstance(value, list):
            existing.extend(value)
        else:
            existing.append(value)
    else:
        if isinstance(value, list):
            target[key] = [existing, *value]
        else:
            target[key] = [existing, value]


def _collect_properties(
    g: Graph,
    subject: URIRef | BNode,
    visited: set[str],
    prefix: str = "",
) -> dict:
    """
    Recursively collect all predicate-object pairs for *subject*.

    When an object is a URI or blank node that itself has triples in the graph
    (i.e., it is a subject), its properties are recursively collected and
    merged into the flat output dict under dot-prefixed keys.

    Parameters
    ----------
    g:       The RDF graph.
    subject: The current subject node.
    visited: Set of already-visited node identifiers (prevents cycles).
    prefix:  Dot-notation prefix accumulated so far.

    Returns
    -------
    A flat ``{key: value}`` properties dictionary.
    """
    properties: dict = {}

    for predicate, obj in g.predicate_objects(subject):
        # Skip rdf:type — handled separately at the entity level
        if predicate == RDF.type:
            continue

        pred_local = _local_name(str(predicate))
        key = f"{prefix}.{pred_local}" if prefix else pred_local

        if isinstance(obj, (URIRef, BNode)):
            obj_id = str(obj)
            # Only recurse if the node has its own triples and hasn't been
            # visited yet (cycle guard)
            has_triples = any(True for _ in g.predicate_objects(obj))
            if has_triples and obj_id not in visited:
                visited.add(obj_id)
                nested = _collect_properties(g, obj, visited, prefix=key)
                for nk, nv in nested.items():
                    _merge(properties, nk, nv)
            else:
                # Leaf URI with no further triples — store the raw URI string
                _merge(properties, key, obj_id)
        else:
            # RDF Literal
            _merge(properties, key, str(obj))

    return properties


def _filter_properties(properties: dict, property_names: list[str]) -> dict:
    """
    Keep only entries whose key exactly matches, or starts with one of the
    given *property_names* (i.e., top-level predicate filter that also retains
    all flattened sub-keys belonging to that predicate).

    Example
    -------
    ``property_names=["hasPrimaryContactPoint"]`` keeps
    ``hasPrimaryContactPoint.email``, ``hasPrimaryContactPoint.telephone``, etc.
    """
    result: dict = {}
    for name in property_names:
        for key, value in properties.items():
            if key == name or key.startswith(name + "."):
                result[key] = value
    return result


def _parse_rdf(rdf_string: str) -> Graph:
    """
    Attempt to parse *rdf_string* trying the most common RDF serialisation
    formats in order: RDF/XML, Turtle, N-Triples, N3, JSON-LD.

    Raises ``ValueError`` if none of them succeeds.
    """
    formats = ["xml", "turtle", "nt", "n3", "json-ld"]
    last_error: Exception | None = None

    for fmt in formats:
        try:
            g = Graph()
            g.parse(data=rdf_string, format=fmt)
            return g
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise ValueError(
        f"Could not parse RDF string in any supported format. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def rdf_entitymention_extractor(
    rdf_string: str,
    entity_type: str,
    origin_id: str,
    request_id: str,
    property_names: list[str] | None = None,
) -> EntityMention | None:
    """
    Extract the first entity mention of the given type from an RDF string.

    All properties of the matching entity are collected into a flat
    ``properties`` dictionary.  References to other nodes in the graph are
    followed recursively and their properties are included using dot-notation
    keys (e.g. ``hasPrimaryContactPoint.email``).

    Parameters
    ----------
    rdf_string:     An RDF document as a string (RDF/XML, Turtle, N-Triples,
                    N3, or JSON-LD).
    entity_type:    URI of the ``rdf:type`` to extract.
    origin_id:      Unique identifier for the data origin, used for tracking.
    request_id:     Client-assigned request identifier, used for tracking.
    property_names: Optional list of top-level predicate local-names to include.
                    Only properties whose key exactly matches one of the names,
                    or starts with ``<name>.``, will be present in the output.
                    When ``None`` (default), all properties are returned.

    Returns
    -------
    An :class:`EntityMention` instance, or ``None`` if no entity of the given
    type is found or if any error occurs during parsing or extraction.
    """
    try:
        g = _parse_rdf(rdf_string)
    except Exception as exc:  # noqa: BLE001
        print(f"[rdf-entitymention-extractor] Error parsing RDF string: {exc}")
        return None

    try:
        type_uri = URIRef(entity_type)
        for subject in g.subjects(RDF.type, type_uri):
            subject_id = str(subject)
            visited: set[str] = {subject_id}
            properties = _collect_properties(g, subject, visited)

            if property_names is not None:
                properties = _filter_properties(properties, property_names)

            return EntityMention(
                origin_id=origin_id,
                request_id=request_id,
                entity_type=entity_type,
                original_asset=subject_id,
                properties=properties,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[rdf-entitymention-extractor] Error extracting entity mention: {exc}")
        return None

    # No matching entity found
    return None
