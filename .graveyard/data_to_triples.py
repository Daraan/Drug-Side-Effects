"""Convert the loaded entries to sensefull triple combinations"""

from preprocessing import load_data

# NOTE: drugbank ids can be dereferences as http://bio2rdf.org/drugbank:DB00001


def process_mappings():
    for line in load_data.load_drug_mappings():
        (drugbankId, name, ttd_id, pubchem_cid, cas_num, chembl_id, zinc_id,
         chebi_id, kegg_cid, kegg_id, bindingDB_id, UMLS_cuis,
         stitch_id) = line
        triples = []
        if drugbankId:
            triples.append(("drugbankId"))
