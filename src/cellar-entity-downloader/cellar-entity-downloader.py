import logging
import os
import re
import time
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSON
from rdflib import Graph, Namespace, RDF, OWL

# --- BATCH PARAMETERS ---
SKIP = 2600      # Start at this record (OFFSET)
LIMIT = 400   # Number of records to process in this run

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

def get_organization_uris(skip, limit):
    sparql = SPARQLWrapper(ENDPOINT_URL)
    query = f"""
    {SPARQL_PREFIXES}
    PREFIX org: <http://www.w3.org/ns/org#> PREFIX epo: <http://data.europa.eu/a4g/ontology#> SELECT DISTINCT ?name ?org WHERE {{ ?org a org:Organization ; epo:hasLegalName ?name .}}
    ORDER BY ?org OFFSET {skip} LIMIT {limit}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["org"]["value"] for result in results["results"]["bindings"]]

def fetch_and_save(org_uri, index, batch_total):
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
        if not raw_data or len(raw_data) < 10: return
        
        g = Graph()
        g.parse(data=raw_data, format="turtle")
        for p, u in PREFIX_MAP.items(): g.bind(p, Namespace(u))
        g.remove((None, RDF.type, OWL.Class))
        
        file_id = org_uri.split('/')[-1].split('#')[-1]
        filename = re.sub(r'[^a-zA-Z0-9]', '_', file_id) + ".ttl"
        
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(g.serialize(format="turtle"))
        
        logger.info("[%d/%d] SAVED: %s", index, batch_total, filename)
    except Exception:
        logger.error("[%d/%d] FAILED: %s", index, batch_total, org_uri)

def main():
    logger.info("Connecting to EU Publications Office...")
    total_in_store = get_total_count()
    logger.info("Total Organizations in Store: %s", total_in_store)

    uris = get_organization_uris(SKIP, LIMIT)
    batch_size = len(uris)
    logger.info("Running Batch: SKIP %d, LIMIT %d (Processing %d records)\n%s", SKIP, LIMIT, batch_size, "-"*50)

    for i, uri in enumerate(uris, start=1):
        fetch_and_save(uri, i, batch_size)
        time.sleep(0.2)

if __name__ == "__main__":
    main()