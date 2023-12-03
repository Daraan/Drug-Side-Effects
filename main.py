import argparse
import pandas as pd
import rdflib
import kg_backend
import query_strings as qs


def run_server():
    from flask_frontend import app
    app.run(host='0.0.0.0', port=81)


def prepare_kgproject(test=True):
    # Load the class
    global kb
    if test:
        kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl",
                                      "files/db_terms_bridge.ttl",
                                      "files/SNAP-A-Box_test.ttl")
    else:
        import time
        start = time.time()
        kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl",
                                      "files/db_terms_bridge.ttl",
                                      "files/SNAP-A-Box-prefixed.ttl")
        print("Loading took: ", time.time() - start)

    return kb


def runquery(query):
    # query could be list of medicienes
    results = kb.query(query)
    # TODO: could be nicer
    print("\n".join(str(r) for r in results))


if __name__ == "__main__":
    test = True
    kb = prepare_kgproject(test=True)
    # or argparse instead of input

    if test:
        drugs = ["CID000002173", "CID000003345", "CID003062316"]
    else:
        # 'Acetylsalicylic acid': CID000002244
        # Ibuprofen: CID000003672
        # Paracetamol 'Acetaminophen': CID000001983
        #
        # drugs =["CID000002244", "CID000003672", "CID000001983"]
        drugs = ["CID000002244", "CID000003672", "CID000001983"]

    print("Query drugs: ", *drugs)
    results = kb.side_effects_drug_list(*drugs)
    print("Side effects:")
    print("\n".join(r["side_effect_term"] for r in results))

    print("\n-------------------------\n")

    drugs = input(
        "Give a druglist (STITCH IDs) yourself, use spaces to separate: "
    ).split(" ")

    runquery(input("Write your query: "))
