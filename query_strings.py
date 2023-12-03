# from namespace import *

# Must match bewlow
STITCH_NAMESPACE = ""
DB_VOC = "db_voc"
DB = "db"
SIDER = "sider"


# NOTE SPARQL no @ and no .
PREFIXE = f"""
prefix : <http://example.org/> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix dcterms: <http://purl.org/dc/terms/> 
prefix db_voc: <http://bio2rdf.org/drugbank_vocabulary:> 
prefix db: <http://bio2rdf.org/drugbank:>
prefix sider: <http://bio2rdf.org/sider_vocabulary:> 
prefix umls: <http://bio2rdf.org/umls:> 

"""

# 1) create a query template with the UPPERCASE words from fstrings
# Single brackets are filled with global variables e.g. {{STITCH_NAMESPACE}} -> "stitch"
# Double brackets are reduced to single brackets to be filled in step 2), e.g {{stich_id}} -> {stitch_id}
# SYNTAX brackets have to be writen as quadruple brackets {{{{ reduced to double brackets -> {{

# 2) use str.format(key=value): Replaces keywords with their values {{key}}-> value
# Syntax brackets are here double brackets reduced to single ones {{ -> { for the syntax

# TODO, CHECK might need to use VALUES:
# https://www.w3.org/TR/sparql11-query/#inline-data

# Get the side effects of a single drug
_string_side_effects_single = PREFIXE + """
SELECT ?side_effect_source ?side_effect_code ?side_effect_term
WHERE {{
    VALUES ?side_effect_source {{ {STITCH_NAMESPACE}:{stitch_id}  }} .
    ?side_effect_source {SIDER_VOC}:side-effect ?side_effect_code .
    ?side_effect_code {SIDER_VOC}:preferred-term ?side_effect_term .
}}"""


def sideeffect_single_drug(stitch_id):
    """
    For example yields such a query to be used:
    >>> print(make_query_for_single(C123))

    SELECT stich:C123 ?side_effect_code ?side_effect_term
    WHERE {
            stich:C123 db_voc:side-effect ?side_effect_code .
            ?side_effect_code : sider_voc:preferred-term ?side_effect_term 
    }
    """
    # NOTE here globals are injected via format
    return _string_side_effects_single.format(
        stitch_id=stitch_id,
        STITCH_NAMESPACE=STITCH_NAMESPACE,
        DB_VOC=DB_VOC,
        SIDER_VOC=SIDER)


# Returns the individual side-effects of multiple drugs.
# Untested!
_string_side_effects_of_multiple_drugs_without_interactions = """
SELECT ?side_effect_source ?side_effect_code ?side_effect_term 
WHERE {{
    VALUES ?side_effect_source {{all_drugs}}
    ?side_effect_source {SIDER_VOC}:side-effect ?side_effect_code .
    ?side_effect_code {SIDER_VOC}:preferred-term ?side_effect_term .
}}
"""


def individual_side_effects(*ids):
    NotImplemented


# NOTE here globals are replaced during string creation -> doubled brackets
# Get the side effects of a drug-drug-combination.
_string_drug_drug_interactions = PREFIXE + f"""
SELECT ?side_effect_source ?side_effect_code ?side_effect_term
    WHERE {{{{
        VALUES ?s1 {{{{ {STITCH_NAMESPACE}:{{stitch_id}}  }}}} .
        VALUES ?id2 {{{{  {{other_drugs}}   }}}} .
        ?s1 {DB_VOC}:ddi-interactor-in ?side_effect_source .
        ?id2 {DB_VOC}:ddi-interactor-in ?side_effect_source .
        
        ?side_effect_source {SIDER}:side-effect ?side_effect_code .
        ?side_effect_code {SIDER}:preferred-term ?side_effect_term .
    }}}}
"""


def sideeffect_drug_drug(stitch_id1, stitch_id2):
    return _string_drug_drug_interactions.format(stitch_id=stitch_id1,
                                                 other_drugs=STITCH_NAMESPACE +
                                                 ":" + stitch_id2)


# BETTER query make UNION of SIDE codes
# use (stitch_id or side_side_from_ids)

# For a single drug, get its own and all that interact with it.
_string_drug_side_effects_with_interactions = PREFIXE + f"""
SELECT * WHERE
{{{{
  {{{{
    SELECT ?side_effect_source ?side_effect_code ?side_effect_term
    WHERE {{{{
        VALUES ?side_effect_source {{{{ {STITCH_NAMESPACE}:{{stitch_id}}  }}}} 
        ?side_effect_source {SIDER}:side-effect ?side_effect_code .
        ?side_effect_code {SIDER}:preferred-term ?side_effect_term .
    }}}}
  }}}}
  UNION
  {{{{
    SELECT ?side_effect_source ?side_effect_code ?side_effect_term
    WHERE {{{{
        VALUES ?s1 {{{{ {STITCH_NAMESPACE}:{{stitch_id}}  }}}}
        VALUES ?id2 {{{{  {{other_drugs}}   }}}}
        ?s1 {DB_VOC}:ddi-interactor-in ?side_effect_source .
        ?id2 {DB_VOC}:ddi-interactor-in ?side_effect_source .
        
        ?side_effect_source {SIDER}:side-effect ?side_effect_code .
        ?side_effect_code {SIDER}:preferred-term ?side_effect_term .
    }}}}
  }}}}
}}}}
"""


def drug_side_effect_and_interactions(stitch_id, *other_ids):
    s = _string_drug_side_effects_with_interactions.format(
        stitch_id=stitch_id,
        other_drugs=":" + " :".join(other_ids),  # add : for first
    )
    return s


# IDEA, test which is better:
# Use VALUES for first query as well and two values in 2nd.
# Advantage: NO LOOP in python and a SINGLE query
# Disadvantage: O(n^2) lookup in second query, without a reduction
#     duplicated results for id1->side<-id2 & id2->side<-id1
"""
SELECT ?side_effect_code ?side_effect_term ?side_effect_source WHERE
{{
  {{
    SELECT ?side_effect_code ?side_effect_term {STITCH_NAMESPACE}:{stitch_id} AS ?side_effect_source
    WHERE {{
        VALUES ?side_effect_source {{all_drugs}}
        {STITCH_NAMESPACE}:{stitch_id} {SIDER_VOC}:side-effect ?side_effect_code .
        ?side_effect_code {SIDER_VOC}:preferred-term ?side_effect_term .
    }}
  }}
  UNION
  {{
    SELECT ?side_effect_code ?side_effect_term ?interactor AS ?side_effect_source
    WHERE {{
        VALUES ?id1 {{all_drugs}}
        VALUES ?id2 {{all_drugs}}
        ?id1 {DB_VOC}:ddi-interactor-in ?interactor .
        ?id2 {DB_VOC}:ddi-interactor-in ?interactor .

        ?interactor {SIDER_VOC}:side-effect ?side_effect_code .
        ?side_effect_code {SIDER_VOC}:preferred-term ?side_effect_term.
    }}
  }}
}}
"""


find_connected = PREFIXE + """
     SELECT DISTINCT ?s1 ?s2 ?n1 ?n2 
     WHERE {
         ?db1 <> ?db2 .
         ?db1 dcterms:title ?n1 .
        ?db2 dcterms:title ?n2 .
         ?s1 owl:sameAs ?db1 .
         ?s2 owl:sameAs ?db2 .
         ?s1 db_voc:ddi-interactor-in ?connector .
         ?s2 db_voc:ddi-interactor-in ?connector .
     }
     LIMIT 10
     """

_name_to_stitch = PREFIXE + f"""
    SELECT ?stitch_id
    WHERE {{{{
        VALUES ?name {{{{ "{{name}}"@en }}}}
        ?stitch_id owl:sameAs ?db_id .
        ?db_id dcterms:title ?name .
    }}}} 
"""

_names_to_stitch = PREFIXE + f"""
    SELECT ?stitch_id
    WHERE {{{{
        VALUES ?name {{{{  {{name_list}} }}}}
        ?stitch_id owl:sameAs ?db_id .
        ?db_id dcterms:title ?name .
    }}}} 
"""


def name_to_stitch(name):
    return _name_to_stitch.format(name=name)

def names_to_stitch(*names):
    return _names_to_stitch.format(name_list=" ".join('"'+n+'"@en' for n in names))

_string_drug_side_effects_with_interactions_from_names = PREFIXE + f"""
SELECT * WHERE
{{{{
    VALUES ?name {{{{  {{name_list}} }}}}
    ?stitch_id owl:sameAs ?db_id .
    ?db_id dcterms:title ?name .

    {{{{
        SELECT ?side_effect_source ?side_effect_code ?side_effect_term
        WHERE {{{{
            BIND (?stitch_id AS ?side_effect_source)
            ?stitch_id {SIDER}:side-effect ?side_effect_code .
            ?side_effect_code {SIDER}:preferred-term ?side_effect_term .
        }}}}
    }}}}
    UNION
    {{{{
        SELECT ?side_effect_source ?side_effect_code ?side_effect_term
        WHERE {{{{
            VALUES ?id2 {{{{ ?stitch_id  }}}}
            ?id2 <> ?stitch_id
            ?stitch_id {DB_VOC}:ddi-interactor-in ?side_effect_source .
            ?id2 {DB_VOC}:ddi-interactor-in ?side_effect_source .
            
            ?side_effect_source {SIDER}:side-effect ?side_effect_code .
            ?side_effect_code {SIDER}:preferred-term ?side_effect_term .
        }}}}
    }}}}
}}}}
"""

def all_from_names(*names):
    return _string_drug_side_effects_with_interactions_from_names.format(
        name_list=" ".join('"'+n+'"@en' for n in names),
    )