import rdflib
import kg_backend

kg_backend.DEBUG = False

def run_server():
    from flask_frontend import app
    app.run(host='0.0.0.0', port=8888 if kg_backend.MODE == "test" else 8889)


def runquery(query):
    # query could be list of medicienes
    kb = kg_backend.prepare_kgproject(test=None)
    kg_backend.DEBUG = True
    results = kg_backend.kb.query(query)
    # TODO: could be nicer
    print("\n".join(str(r) for r in results))


if __name__ == "__main__":
    import sys
    print("ARGS: ", sys.argv)
    if "all" in sys.argv:
        kg_backend.MODE = "all"
    else:
        kg_backend.MODE = "test"
    print("MODE: ", kg_backend.MODE)
    if True:
        run_server()
    else:
        print("Server start skipped.")
        test = False
        kb = kg_backend.prepare_kgproject(test=test)
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
        drug_names = ['Acetylsalicylic acid', "Ibuprofen", 'Acetaminophen']

        print("Query drugs: ", *drugs)
        results = kb.side_effects_drug_list(*drugs)
        print("Side effects:")
        print("\n".join(r["side_effect_term"] for r in results))

        print("Query drug names: ", drug_names)
        results = kb.side_effects_of_drug_names(*drug_names)
        print("Side effects:")
        print("\n".join(r["side_effect_term"] for r in results))

    print("\n--------- END ----------------\n")

    #drugs = input(
    #    "Give a druglist (STITCH IDs) yourself, use spaces to separate: "
    #).split(" ")

    #runquery(input("Write your query: "))
