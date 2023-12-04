"""Runs our HTML entry page later on"""
from flask import Flask, render_template, request, Response
import kg_backend
from rdflib.term import Literal

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')



# @app.route("/runquery", methods=["POST"])
# def runquery():
#   data = request.get_json()
#   input1 = data.get("input1")
#   input2 = data.get("input2")

#   # Call your Python function with the provided inputs
#   kb = prepare_kgproject(test=True)
#   # results = kb.sideffect_single_drug(
#   #     input1) if not input2 else kb.sideffect_drug_drug(input1, input2)
#   results = kb.side_effects_of_drug_names(input1, input2)

#   # Extract and format the desired values
#   formatted_results = [
#       str(r) for result in results for r in result if isinstance(r, Literal)
#   ]

#   # Join the formatted results with commas
#   response_text = ", ".join(
#       formatted_results) if formatted_results else 'Not found'

#   return Response(response=response_text,
#                   content_type='text/plain;charset=utf-8')


@app.route('/runquery', methods=['POST'])
def run_query():
  data = request.get_json()
  input_values = data.get('input', '')

  # Process the input values (comma-separated)
  stitch_ids = [id.strip() for id in input_values.split(',')]
  print("Query drugs: ", *stitch_ids)
  kb = kg_backend.prepare_kgproject(test=False)
  # Call your side_effects_drug_list function
  results = kb.side_effects_of_drug_names(*stitch_ids)

  # Extract and format the desired values
  formatted_results = [
      str(r) for result in results for r in result if isinstance(r, Literal)
  ]
  print("Results: ", formatted_results)

  # Join the formatted results with commas
  response_text = ", ".join(
      formatted_results) if formatted_results else 'Not found'

  return Response(response=response_text,
                  content_type='text/plain;charset=utf-8')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)

# if test:
#     drugs = ["CID000002173", "CID000003345", "CID003062316"]
# else:
#     # 'Acetylsalicylic acid': CID000002244
#     # Ibuprofen: CID000003672
#     # Paracetamol 'Acetaminophen': CID000001983
#     #
#     # drugs =["CID000002244", "CID000003672", "CID000001983"]
#     drugs = ["CID000002244", "CID000003672", "CID000001983"]
# drug_names = ['Acetylsalicylic acid', "Ibuprofen", 'Acetaminophen' ]

# print("Query drugs: ", *drugs)
# results = kb.side_effects_drug_list(*drugs)
# results = kb.side_effects_of_drug_names(*drug_names)
# print("Side effects:")
# print("\n".join(r["side_effect_term"] for r in results))

# print("\n-------------------------\n")

# drugs = input(
#     "Give a druglist (STITCH IDs) yourself, use spaces to separate: "
# ).split(" ")

# runquery(input("Write your query: "))
