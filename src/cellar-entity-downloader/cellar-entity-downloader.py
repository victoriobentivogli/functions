import logging
import os
import re
import time
from datetime import datetime, timezone
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSON
from rdflib import Graph, Namespace, RDF, OWL

# --- BATCH PARAMETERS ---
BATCH_SIZE = 1000  # Number of records per batch

# --- CONFIGURATION ---
ENDPOINT_URL = "https://publications.europa.eu/webapi/rdf/sparql"
OUTPUT_DIR = "organization_data"

# --- LOGGING ---
logger = logging.getLogger("cellar-entity-downloader")
logger.setLevel(logging.DEBUG)

_console = logging.StreamHandler()
_console.setLevel(logging.DEBUG)

_entity_file = logging.FileHandler("entities.log", mode="w", encoding="utf-8")
_entity_file.setLevel(logging.DEBUG)

_error_file = logging.FileHandler("error.log", mode="w", encoding="utf-8")
_error_file.setLevel(logging.ERROR)

_fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_console.setFormatter(_fmt)
_entity_file.setFormatter(_fmt)
_error_file.setFormatter(_fmt)

logger.addHandler(_console)
logger.addHandler(_entity_file)
logger.addHandler(_error_file)

PREFIX_MAP = {
    "adms": "http://www.w3.org/ns/adms#",
    "cccev": "http://data.europa.eu/m8g/",
    "dct": "http://purl.org/dc/terms/",
    "epo": "http://data.europa.eu/a4g/ontology#",
    "locn": "http://www.w3.org/ns/locn#",
    "org": "http://www.w3.org/ns/org#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

SPARQL_PREFIXES = "\n".join([f"PREFIX {p}: <{u}>" for p, u in PREFIX_MAP.items()])
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_total_count():
    """Queries the endpoint for the total number of org:Organization instances."""
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = "PREFIX org: <http://www.w3.org/ns/org#> PREFIX epo: <http://data.europa.eu/a4g/ontology#> SELECT (COUNT(DISTINCT ?name) AS ?total)  WHERE { ?org a org:Organization ; epo:hasLegalName ?name .}"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        result = sparql.query().convert()
        return int(result["results"]["bindings"][0]["total"]["value"])
    except:
        return "Unknown"

def get_organization_uris(limit, after_uri=None):
    """Fetch the next batch of organization URIs using cursor-based pagination.

    Uses FILTER (?org > <after_uri>) instead of OFFSET to avoid the
    Virtuoso 10 000-row sorted-output limit.
    """
    sparql = SPARQLWrapper(ENDPOINT_URL)
    filter_clause = f'FILTER (STR(?org) > "{after_uri}")' if after_uri else ""
    query = f"""
    {SPARQL_PREFIXES}
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX epo: <http://data.europa.eu/a4g/ontology#>
    SELECT DISTINCT ?name ?org WHERE {{
        ?org a org:Organization ; epo:hasLegalName ?name .
        {filter_clause}
    }}
    ORDER BY ?org LIMIT {limit}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["org"]["value"] for result in results["results"]["bindings"]]

def fetch_and_save(org_uri, index, total):
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
    {SPARQL_PREFIXES}
    CONSTRUCT {{
        <{org_uri}> ?p ?o .
        ?related ?p2 ?o2 .
    }}
    WHERE {{
        <{org_uri}> ?p ?o .
        OPTIONAL {{
            VALUES ?relProp {{ cccev:registeredAddress epo:hasPrimaryContactPoint adms:identifier epo:hasLegalIdentifier }}
            <{org_uri}> ?relProp ?related .
            ?related ?p2 ?o2 .
        }}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)
    sparql.setTimeout(45)
    
    try:
        raw_data = sparql.query().convert()
        if not raw_data or len(raw_data) < 10: return False
        
        g = Graph()
        g.parse(data=raw_data, format="turtle")
        for p, u in PREFIX_MAP.items(): g.bind(p, Namespace(u))
        g.remove((None, RDF.type, OWL.Class))
        
        file_id = org_uri.split('/')[-1].split('#')[-1]
        filename = re.sub(r'[^a-zA-Z0-9]', '_', file_id) + ".ttl"
        
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(g.serialize(format="turtle"))
        
        logger.info("[%d/%d] SAVED: %s", index, total, filename)
        return True
    except Exception:
        logger.error("[%d/%d] FAILED: %s", index, total, org_uri)
        return False

def main():
    start_time = datetime.now(timezone.utc)
    logger.info("Start time: %s", start_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
    logger.info("Connecting to EU Publications Office...")

    total_in_store = get_total_count()
    logger.info("Total Organizations in Store: %s", total_in_store)
    logger.info("Batch size: %d", BATCH_SIZE)
    logger.info("-" * 50)

    last_uri = None
    batch_num = 0
    processed = 0
    success_count = 0
    error_count = 0

    while True:
        uris = get_organization_uris(BATCH_SIZE, after_uri=last_uri)
        if not uris:
            break

        batch_num += 1
        batch_start = time.monotonic()
        batch_errors = 0
        logger.info("Batch %d: fetching %d records (after %s)", batch_num, len(uris), last_uri or "start")

        for uri in uris:
            processed += 1
            ok = fetch_and_save(uri, processed, total_in_store if isinstance(total_in_store, int) else processed)
            if ok:
                success_count += 1
            else:
                error_count += 1
                batch_errors += 1
            time.sleep(0.2)

        batch_elapsed = time.monotonic() - batch_start
        logger.info("Batch %d done: %.1fs, %d errors, %d total processed", batch_num, batch_elapsed, batch_errors, processed)

        last_uri = uris[-1]
        if len(uris) < BATCH_SIZE:
            break

    end_time = datetime.now(timezone.utc)
    elapsed = (end_time - start_time).total_seconds()
    rate = (processed / elapsed * 60) if elapsed > 0 else 0

    logger.info("-" * 50)
    logger.info("COMPLETED")
    logger.info("  Start time:   %s", start_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
    logger.info("  End time:     %s", end_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
    logger.info("  Elapsed:      %.1f seconds", elapsed)
    logger.info("  Processed:    %d", processed)
    logger.info("  Success:      %d", success_count)
    logger.info("  Errors:       %d", error_count)
    logger.info("  Rate:         %.1f entities/min", rate)

if __name__ == "__main__":
    main()