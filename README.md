# Functions

This repository will be used for the development of some functions for the ERS/ERE project.

## Shared models

### ERE Model (ere-model)

Pydantic models shared across ERE pipeline functions. Provides the `EntityMention` model used by all pipeline stages.

## Functions

### RDF EntityMention Extractor (rdf-entitymention-extractor)

This function receives RDF strings and extracts relevant entity mentions (and sub-entity mentions) for the ERE engine.

### EntityMention Cleaner (entitymention-cleaner)

This function receives an EntityMention and returns a "cleaned" version of it, aimed at facilitating processing by the ERE.

### EntityMention Embedder (entitymention-embedder)

This function calculates embeddings based on some properties, combines them according to given weights and adjusts their scale.

### DB Manager (db-manager)

This set of functions provides database operations for EntityMention persistence.

### EntityMention Clusterer (entitymention-clusterer)

This function calculates clusters from EntityMention embeddings.
