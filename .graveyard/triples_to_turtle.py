from preprocessing import data_to_triples as to_triples

# NAMESPACES TO USE

RDF = "rdf"
RDFS = "rdfs"
DCTERMS = "dcterms"
OWL = "owl"

# Note there is <http://bio2rdf.org/drugbank_vocabulary:Drug-Drug-Interaction>


def mapping_triples():
    i = 0
    for stitch_id, name in to_triples:
        # NOTE: Maybe want to also have drugbankid here
        if "null" not in stitch_id:
            i += 1
            print("Loaded STICH ids -> name mappings", i, end="\r")
            yield (stitch_id, "foaf:name", name)


def drug_side_tripples():
    for STITCH, Individual_Side_Effect, _ in to_triples.load_monopharmacy():
        yield (STITCH, STITCH_NAMESPACE + Individual_Side_Effect, STITCH)
