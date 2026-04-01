"""
Tests for rdf_entitymention_extractor.py

Fixtures are based on the EPO (European Procurement Ontology) Organization
entities described in SPECIFICATIONS.md, using the exact structure of a real
TED/eForms procurement notice.
"""

import pytest
from entitymention import EntityMention
from rdf_entitymention_extractor import rdf_entitymention_extractor


# ---------------------------------------------------------------------------
# URI / type constants
# ---------------------------------------------------------------------------

ORG_TYPE     = "http://www.w3.org/ns/org/Organization"
CONTACT_TYPE = "http://data.europa.eu/m8g/ContactPoint"

# Notice ID used in SPECIFICATIONS.md
_NOTICE = "04e04ecb-578c-496a-b40a-7e7b1643303c-01"
_BASE   = f"http://data.europa.eu/a4g/resource/{_NOTICE}"

# Primary organisation
ORG_URI      = f"{_BASE}/Organization/ORG-0001"

# Sub-resources of the primary organisation
LEGAL_ID_URI = (
    f"{_BASE}/Organization/Identifier$_ContractNotice1_UBLExtensions1"
    "_UBLExtension1_ExtensionContent1_EformsExtension1_Organizations1"
    "_Organization1_Company1_PartyLegalEntity1"
)
CONTACT_URI  = (
    f"{_BASE}/CompanyContactPoint$_ContractNotice1_UBLExtensions1"
    "_UBLExtension1_ExtensionContent1_EformsExtension1_Organizations1"
    "_Organization1_Company1_Contact1"
)
ADDRESS_URI  = (
    f"{_BASE}/CompanyAddress$_ContractNotice1_UBLExtensions1"
    "_UBLExtension1_ExtensionContent1_EformsExtension1_Organizations1"
    "_Organization1_Company1_PostalAddress1"
)
ADMS_ID_URI  = f"{_BASE}/Identifier/ORG-0001"

# A second notice / organisation (for cycle-detection tests)
_NOTICE2    = "7a3b9c2d-0e1f-4a5b-8c6d-9e0f1a2b3c4d-01"
_BASE2      = f"http://data.europa.eu/a4g/resource/{_NOTICE2}"
ORG2_URI    = f"{_BASE2}/Organization/ORG-0002"

# Default tracking identifiers for tests
TEST_ORIGIN  = "test-origin"
TEST_REQUEST = "test-request"

# Shared Turtle prefix block
_PREFIXES = """\
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix org:   <http://www.w3.org/ns/org/> .
@prefix epo:   <http://data.europa.eu/a4g/ontology#> .
@prefix cccev: <http://data.europa.eu/m8g/> .
@prefix adms:  <http://www.w3.org/ns/adms#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix locn:  <http://www.w3.org/ns/locn#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
"""


# ---------------------------------------------------------------------------
# RDF fixtures
# ---------------------------------------------------------------------------

# Single Organisation with all sub-resources (mirrors SPECIFICATIONS.md exactly)
ORG_SINGLE_TURTLE = _PREFIXES + f"""
<{ORG_URI}> a org:Organization ;
    epo:hasBuyerLegalType <http://publications.europa.eu/resource/authority/buyer-legal-type/ra> ;
    epo:hasLegalIdentifier <{LEGAL_ID_URI}> ;
    epo:hasLegalName "FORSYNING HELSINGØR A/S"@da ;
    epo:hasMainActivity <http://publications.europa.eu/resource/authority/main-activity/gen-pub> ;
    epo:hasPrimaryContactPoint <{CONTACT_URI}> ;
    cccev:registeredAddress <{ADDRESS_URI}> ;
    adms:identifier <{ADMS_ID_URI}> .

<{LEGAL_ID_URI}> a adms:Identifier ;
    skos:notation "32059325" .

<{CONTACT_URI}> a cccev:ContactPoint ;
    epo:hasContactName "Charlotte Nordberg" ;
    epo:hasInternetAddress "https://www.fh.dk/"^^xsd:anyURI ;
    cccev:email "cnor@servia.dk" ;
    cccev:telephone "4576962100" .

<{ADDRESS_URI}> a locn:Address ;
    epo:hasCountryCode <http://publications.europa.eu/resource/authority/country/DNK> ;
    epo:hasNutsCode <http://data.europa.eu/nuts/code/DK013> ;
    locn:fullAddress "Energivej 25, Helsingør, 3000, DNK" ;
    locn:postCode "3000" ;
    locn:postName "Helsingør" .

<{ADMS_ID_URI}> a adms:Identifier ;
    epo:hasScheme "organization" ;
    skos:notation "ORG-0001" .
"""

# Two Organisations referencing each other — cycle-guard test
ORG_CYCLIC_TURTLE = _PREFIXES + f"""
<{ORG_URI}> a org:Organization ;
    epo:hasLegalName "FORSYNING HELSINGØR A/S"@da ;
    epo:hasSubOrganizationOf <{ORG2_URI}> .

<{ORG2_URI}> a org:Organization ;
    epo:hasLegalName "ACME Procurement GmbH"@de ;
    epo:hasSubOrganizationOf <{ORG_URI}> .
"""

# Same single org in RDF/XML for format-support test
ORG_SINGLE_XML = f"""\
<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:org="http://www.w3.org/ns/org/"
    xmlns:epo="http://data.europa.eu/a4g/ontology#"
    xmlns:adms="http://www.w3.org/ns/adms#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:cccev="http://data.europa.eu/m8g/"
    xmlns:locn="http://www.w3.org/ns/locn#">

  <rdf:Description rdf:about="{ORG_URI}">
    <rdf:type rdf:resource="http://www.w3.org/ns/org/Organization"/>
    <epo:hasLegalName xml:lang="da">FORSYNING HELSINGØR A/S</epo:hasLegalName>
    <epo:hasLegalIdentifier rdf:resource="{LEGAL_ID_URI}"/>
    <adms:identifier rdf:resource="{ADMS_ID_URI}"/>
    <epo:hasPrimaryContactPoint rdf:resource="{CONTACT_URI}"/>
  </rdf:Description>

  <rdf:Description rdf:about="{LEGAL_ID_URI}">
    <rdf:type rdf:resource="http://www.w3.org/ns/adms#Identifier"/>
    <skos:notation>32059325</skos:notation>
  </rdf:Description>

  <rdf:Description rdf:about="{ADMS_ID_URI}">
    <rdf:type rdf:resource="http://www.w3.org/ns/adms#Identifier"/>
    <epo:hasScheme>organization</epo:hasScheme>
    <skos:notation>ORG-0001</skos:notation>
  </rdf:Description>

  <rdf:Description rdf:about="{CONTACT_URI}">
    <rdf:type rdf:resource="http://data.europa.eu/m8g/ContactPoint"/>
    <epo:hasContactName>Charlotte Nordberg</epo:hasContactName>
    <cccev:email>cnor@servia.dk</cccev:email>
  </rdf:Description>
</rdf:RDF>
"""


# ---------------------------------------------------------------------------
# Basic extraction
# ---------------------------------------------------------------------------


class TestBasicExtraction:
    def test_returns_entitymention(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert isinstance(result, EntityMention)

    def test_result_is_not_none(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result is not None

    def test_entitymention_has_required_fields(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert hasattr(result, "origin_id")
        assert hasattr(result, "request_id")
        assert hasattr(result, "entity_type")
        assert hasattr(result, "original_asset")
        assert hasattr(result, "properties")

    def test_entity_type_is_correct(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.entity_type == ORG_TYPE

    def test_origin_id_is_correct(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.origin_id == TEST_ORIGIN

    def test_request_id_is_correct(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.request_id == TEST_REQUEST

    def test_original_asset_is_entity_uri(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.original_asset == ORG_URI

    def test_legal_name(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasLegalName"] == "FORSYNING HELSINGØR A/S"

    def test_buyer_legal_type_stored_as_leaf_uri(self):
        """Authority URIs with no further triples should be stored verbatim."""
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasBuyerLegalType"] == (
            "http://publications.europa.eu/resource/authority/buyer-legal-type/ra"
        )

    def test_main_activity_stored_as_leaf_uri(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasMainActivity"] == (
            "http://publications.europa.eu/resource/authority/main-activity/gen-pub"
        )

    def test_unknown_type_returns_none(self):
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, "http://example.org/UnknownType", TEST_ORIGIN, TEST_REQUEST
        )
        assert result is None

    def test_entity_id_is_auto_generated(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.entity_id  # non-empty SHA256

    def test_ml_fields_have_defaults(self):
        """Extractor should leave ML fields at their defaults."""
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.embedding == []
        assert result.cluster_id == ""
        assert result.similarity_score == 0.0
        assert result.confidence_score == 0.0
        assert result.is_medoid is False


# ---------------------------------------------------------------------------
# Reference flattening
# ---------------------------------------------------------------------------


class TestReferenceFlattening:
    """
    All sub-resources (Identifier, ContactPoint, Address) linked from the
    Organisation should be traversed and their properties merged into the
    top-level properties dict under dot-notation keys.
    """

    # -- adms:Identifier (legal identifier) ----------------------------------

    def test_legal_identifier_notation(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasLegalIdentifier.notation") == "32059325"

    # -- adms:Identifier (ADMS identifier) ------------------------------------

    def test_adms_identifier_notation(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("identifier.notation") == "ORG-0001"

    def test_adms_identifier_scheme(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("identifier.hasScheme") == "organization"

    # -- cccev:ContactPoint ---------------------------------------------------

    def test_contact_name(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.hasContactName") == "Charlotte Nordberg"

    def test_contact_email(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.email") == "cnor@servia.dk"

    def test_contact_telephone(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.telephone") == "4576962100"

    def test_contact_internet_address(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.hasInternetAddress") == "https://www.fh.dk/"

    # -- locn:Address --------------------------------------------------------

    def test_address_full_address(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("registeredAddress.fullAddress") == (
            "Energivej 25, Helsingør, 3000, DNK"
        )

    def test_address_post_code(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("registeredAddress.postCode") == "3000"

    def test_address_post_name(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("registeredAddress.postName") == "Helsingør"

    def test_address_country_code_is_leaf_uri(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("registeredAddress.hasCountryCode") == (
            "http://publications.europa.eu/resource/authority/country/DNK"
        )

    def test_address_nuts_code_is_leaf_uri(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("registeredAddress.hasNutsCode") == (
            "http://data.europa.eu/nuts/code/DK013"
        )


# ---------------------------------------------------------------------------
# Property name filtering
# ---------------------------------------------------------------------------


class TestPropertyNameFiltering:
    """
    The optional ``property_names`` argument restricts which top-level
    predicates (and their flattened sub-keys) are included in the output.
    """

    def test_no_filter_returns_all_properties(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        props = result.properties
        assert "hasLegalName" in props
        assert "registeredAddress.fullAddress" in props
        assert "hasPrimaryContactPoint.email" in props

    def test_single_literal_property_filter(self):
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST, property_names=["hasLegalName"]
        )
        props = result.properties
        assert props == {"hasLegalName": "FORSYNING HELSINGØR A/S"}

    def test_nested_property_filter_includes_sub_keys(self):
        """Filtering on 'hasPrimaryContactPoint' keeps all .* sub-keys."""
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST,
            property_names=["hasPrimaryContactPoint"],
        )
        props = result.properties
        assert "hasPrimaryContactPoint.email" in props
        assert "hasPrimaryContactPoint.telephone" in props
        assert "hasPrimaryContactPoint.hasContactName" in props
        assert "hasLegalName" not in props
        assert "registeredAddress.fullAddress" not in props

    def test_multiple_property_names_filter(self):
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE,
            ORG_TYPE,
            TEST_ORIGIN,
            TEST_REQUEST,
            property_names=["hasLegalName", "identifier"],
        )
        props = result.properties
        assert "hasLegalName" in props
        assert "identifier.notation" in props
        assert "identifier.hasScheme" in props
        assert "registeredAddress.fullAddress" not in props

    def test_empty_property_names_returns_empty_properties(self):
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST, property_names=[]
        )
        assert result.properties == {}

    def test_nonexistent_property_name_returns_empty_properties(self):
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST,
            property_names=["doesNotExist"],
        )
        assert result.properties == {}

    def test_filter_preserves_origin_id_and_type(self):
        """Filtering only affects properties, not origin_id or entity_type."""
        result = rdf_entitymention_extractor(
            ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST,
            property_names=["hasLegalName"],
        )
        assert result.origin_id == TEST_ORIGIN
        assert result.entity_type == ORG_TYPE


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------


class TestCycleDetection:
    """
    ORG-0001 and ORG-0002 point to each other via epo:hasSubOrganizationOf.
    The extractor must not recurse infinitely.
    """

    def test_cyclic_references_do_not_loop_forever(self):
        result = rdf_entitymention_extractor(ORG_CYCLIC_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert isinstance(result, EntityMention)
        assert result is not None

    def test_cyclic_entity_has_legal_name(self):
        result = rdf_entitymention_extractor(ORG_CYCLIC_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert "hasLegalName" in result.properties

    def test_cyclic_entity_has_original_asset(self):
        result = rdf_entitymention_extractor(ORG_CYCLIC_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.original_asset in (ORG_URI, ORG2_URI)


# ---------------------------------------------------------------------------
# Format support
# ---------------------------------------------------------------------------


class TestFormatSupport:
    def test_turtle_parses_correctly(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result is not None

    def test_rdf_xml_parses_correctly(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_XML, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result is not None

    def test_rdf_xml_legal_name(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_XML, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasLegalName"] == "FORSYNING HELSINGØR A/S"

    def test_rdf_xml_identifier_flattened(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_XML, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("identifier.notation") == "ORG-0001"

    def test_rdf_xml_contact_email_flattened(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_XML, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.email") == "cnor@servia.dk"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_malformed_rdf_returns_none(self):
        result = rdf_entitymention_extractor(
            "this is not RDF at all <<<", ORG_TYPE, TEST_ORIGIN, TEST_REQUEST
        )
        assert result is None

    def test_malformed_rdf_prints_error(self, capsys):
        rdf_entitymention_extractor("not rdf <<<", ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        captured = capsys.readouterr()
        assert "[rdf-entitymention-extractor]" in captured.out

    def test_empty_string_returns_none(self):
        result = rdf_entitymention_extractor("", ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result is None


# ---------------------------------------------------------------------------
# JSON-LD format support
# ---------------------------------------------------------------------------


ORG_SINGLE_JSONLD = """{
  "@context": {
    "rdf":   "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "org":   "http://www.w3.org/ns/org/",
    "epo":   "http://data.europa.eu/a4g/ontology#",
    "adms":  "http://www.w3.org/ns/adms#",
    "skos":  "http://www.w3.org/2004/02/skos/core#"
  },
  "@id": "http://data.europa.eu/a4g/resource/notice-jsonld/Organization/ORG-J1",
  "@type": "org:Organization",
  "epo:hasLegalName": "JSON-LD Org",
  "adms:identifier": {
    "@id": "http://data.europa.eu/a4g/resource/notice-jsonld/Identifier/J1",
    "@type": "adms:Identifier",
    "epo:hasScheme": "organization",
    "skos:notation": "ORG-J1"
  }
}"""


class TestJsonLdFormatSupport:
    def test_jsonld_parses_correctly(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_JSONLD, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result is not None

    def test_jsonld_legal_name(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_JSONLD, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasLegalName"] == "JSON-LD Org"

    def test_jsonld_identifier_flattened(self):
        result = rdf_entitymention_extractor(ORG_SINGLE_JSONLD, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("identifier.notation") == "ORG-J1"


# ---------------------------------------------------------------------------
# Multi-valued properties
# ---------------------------------------------------------------------------


MULTI_VALUE_TURTLE = _PREFIXES + """
<http://data.europa.eu/a4g/resource/notice-mv/Organization/ORG-MV>
    a org:Organization ;
    epo:hasLegalName "Name One"@en ;
    epo:hasLegalName "Name Two"@fr .
"""


class TestMultiValuedProperties:
    """Same predicate appearing multiple times should produce a list."""

    def test_multi_valued_property_returns_list(self):
        result = rdf_entitymention_extractor(MULTI_VALUE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        value = result.properties["hasLegalName"]
        assert isinstance(value, list)
        assert len(value) == 2

    def test_multi_valued_property_contains_all_values(self):
        result = rdf_entitymention_extractor(MULTI_VALUE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        value = result.properties["hasLegalName"]
        assert "Name One" in value
        assert "Name Two" in value


# ---------------------------------------------------------------------------
# Blank node handling
# ---------------------------------------------------------------------------


BNODE_TURTLE = _PREFIXES + """
<http://data.europa.eu/a4g/resource/notice-bn/Organization/ORG-BN>
    a org:Organization ;
    epo:hasLegalName "BNode Org" ;
    epo:hasPrimaryContactPoint [
        a cccev:ContactPoint ;
        cccev:email "bn@example.org" ;
        cccev:telephone "1234567890"
    ] .
"""


class TestBlankNodeHandling:
    """Blank nodes (anonymous resources) should be traversed like named URIs."""

    def test_bnode_contact_email_is_flattened(self):
        result = rdf_entitymention_extractor(BNODE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.email") == "bn@example.org"

    def test_bnode_contact_telephone_is_flattened(self):
        result = rdf_entitymention_extractor(BNODE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties.get("hasPrimaryContactPoint.telephone") == "1234567890"

    def test_bnode_entity_has_legal_name(self):
        result = rdf_entitymention_extractor(BNODE_TURTLE, ORG_TYPE, TEST_ORIGIN, TEST_REQUEST)
        assert result.properties["hasLegalName"] == "BNode Org"


# ---------------------------------------------------------------------------
# EntityMention model validation
# ---------------------------------------------------------------------------


class TestEntityMentionModel:
    """Verify Pydantic validation on the EntityMention model itself."""

    def test_valid_entitymention_construction(self):
        e = EntityMention(
            origin_id="http://example.org/origin",
            request_id="req-001",
            entity_type="http://example.org/Type",
            original_asset="http://example.org/1",
            properties={"name": "test"},
        )
        assert e.origin_id == "http://example.org/origin"
        assert e.entity_type == "http://example.org/Type"
        assert e.properties == {"name": "test"}

    def test_properties_accept_list_values(self):
        e = EntityMention(
            origin_id="x", request_id="r", entity_type="t",
            original_asset="a", properties={"k": ["a", "b"]},
        )
        assert e.properties["k"] == ["a", "b"]

    def test_missing_field_raises_validation_error(self):
        with pytest.raises(Exception):
            EntityMention(origin_id="x", request_id="r", entity_type="t")

    def test_entitymention_is_immutable(self):
        e = EntityMention(
            origin_id="x", request_id="r", entity_type="t",
            original_asset="a", properties={"k": "v"},
        )
        with pytest.raises(Exception):
            e.origin_id = "y"
