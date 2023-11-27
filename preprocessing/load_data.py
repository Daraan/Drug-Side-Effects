"""
Open files and functions to return triples in an iterative way, i.e., they return generators to be iterated over to keep the memory lower and they can be more efficiently pipelined into the next steps.
"""

import pandas as pd
from collections import namedtuple

Mapping = namedtuple("Mapping", "drugbankId	name	ttd_id	pubchem_cid	cas_num	chembl_id	zinc_id"\
                                "chebi_id	kegg_cid	kegg_id	bindingDB_id	UMLS_cuis	stitch_id".split("\t"))


def null_as_None(s):
    return None if s == "null" else s


def pd_open_mapping():
    """
    Schema:
    # drugbankId	name	ttd_id	pubchem_cid	cas_num	chembl_id	zinc_id	chebi_id	kegg_cid	kegg_id	bindingDB_id	UMLS_cuis	stitch_id
    # DB13088	AZD-0424	D0QG8F	9893171	692054-06-1	CHEMBL3545177	null	null	null	null	null	C4519307	null
    """
    drug_mappings = pd.read_csv("files/drug-mappings.tsv", sep="\t")
    return drug_mappings


def load_drug_mappings():
    with open("files/drug-mappings.tsv", "r") as f:
        header = f.readline()
        print(header)
        for line in f:
            #(drugbankId, name, ttd_id, pubchem_cid, cas_num, chembl_id,
            # zinc_id, chebi_id, kegg_cid, kegg_id, bindingDB_id, UMLS_cuis,
            # stitch_id) = map(null_as_None, line.strip().split("\t"))
            #yield (drugbankId, name, ttd_id, pubchem_cid, cas_num, chembl_id,
            #       zinc_id, chebi_id, kegg_cid, kegg_id, bindingDB_id,
            #       UMLS_cuis, stitch_id)
            yield Mapping._make(
                map(null_as_None,
                    line.strip().split("\t"))
            )  # will have fileds named like above, e.g. mapping.drugbankId


# -----------------------------------


def pd_open_drug_sideeffects():
    # STITCH,Individual Side Effect,Side Effect Name
    # CID003062316,C1096328,central nervous system mass
    drug_side = pd.read_csv("files/ChSe-Decagon_monopharmacy.csv", sep=",")
    return drug_side


def load_monopharmacy():  # as generator/ iterable
    with open("files/ChSe-Decagon_monopharmacy.csv", "r") as f:
        for line in f:
            STITCH, Individual_Side_Effect, Side_Effect_Name = line.split(",")
            yield STITCH, Individual_Side_Effect, Side_Effect_Name


# ---------


def pd_load_polypharmacy():
    # STITCH 1,STITCH 2,Polypharmacy Side Effect,Side Effect Name
    # CID000002173,CID000003345,C0151714,hypermagnesemia
    polypharmacy = pd.read_csv("files/ChChSe-Decagon_polypharmacy.csv",
                               sep=",")
    return polypharmacy


def load_polypharmacy():
    with open("files/ChChSe-Decagon_polypharmacy.csv", "r") as f:
        header = f.readline()
        print(header)
        for line in f:
            STITCH_1, STITCH_2, Polypharmacy_Side_Effect, Side_Effect_Name = line.split(
                ",")
            yield STITCH_1, STITCH_2, Polypharmacy_Side_Effect, Side_Effect_Name


# -------------------------


def pd_load_drug_drug():
    # Might not be so useful as it only contains two IDs
    #DB00862	DB00966
    drug_drug_side2 = pd.read_csv("files/ChCh-Miner_durgbank-chem-chem.tsv",
                                  sep="\t",
                                  header=None)
    return drug_drug_side2


def load_drug_drug():
    with open("files/ChCh-Miner_durgbank-chem-chem.tsv", "r") as f:
        for line in f:
            id1, id2 = line.split("\t")
            yield id1, id2


def load_dataframes():
    drug_mappings = pd_open_mapping()
    monopharmacy = pd_open_drug_sideeffects()
    polypharmacy = pd_load_polypharmacy()
    drug_drug_side = pd_load_drug_drug()
    return drug_mappings, monopharmacy, polypharmacy, drug_drug_side
