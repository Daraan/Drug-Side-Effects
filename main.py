import argparse
import pandas as pd
import rdflib
import kg_backend



def run_server():
    from flask_frontend import app
    app.run(host='0.0.0.0', port=81)


def prepare_kgproject(test=True):
    # Load the class
    global kb
    if test:
        kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl", "files/db_terms_bridge.ttl",
                                      "files\SNAP-A-Box_test.ttl")
    else:
        kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl", "files/db_terms_bridge.ttl",
                                      "files/SNAP-A-Box.ttl")
    return kb


def runquery(query):
    # query could be list of medicienes
    results = kb.query(query)
    # TODO: could be nicer
    print("\n".join(str(r) for r in results))


if __name__ == "__main__":
    kb = prepare_kgproject()
    # or argparse instead of input
    drugs = ["CID000002173", "CID000003345", "CID003062316"]
    print("Query drugs: ", *drugs)
    results = kb.side_effects_drug_list(*drugs)
    print("Side effects:")
    print("\n".join(r["side_effect_term"] for r in results))
    drugs = input(
        "Give a druglist (STITCH IDs) yourself, use spaces to separate:"
    ).split(" ")
    runquery(input("Write your query: "))
# 