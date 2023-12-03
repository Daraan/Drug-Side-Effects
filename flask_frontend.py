"""Runs our HTML entry page later on"""
from flask import Flask, render_template, request, Response
import kg_backend
from rdflib.term import Literal

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


def prepare_kgproject(test=True):
  # Load the class
  global kb
  if test:
    kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl",
                                  "files/db_terms_bridge.ttl",
                                  "files/SNAP-A-Box_test.ttl")
  else:
    kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl",
                                  "files/SNAP-A-Box.ttl")
  return kb


@app.route("/runquery", methods=["POST"])
def runquery():
  data = request.get_json()
  input1 = data.get("input1")
  input2 = data.get("input2")

  # Call your Python function with the provided inputs
  kb = prepare_kgproject(test=True)
  # results = kb.sideffect_single_drug(
  #     input1) if not input2 else kb.sideffect_drug_drug(input1, input2)
  results = kb.side_effects_drug_list(input1, input2)

  # Extract and format the desired values
  formatted_results = [
      str(r) for result in results for r in result if isinstance(r, Literal)
  ]

  # Join the formatted results with commas
  response_text = ", ".join(
      formatted_results) if formatted_results else 'Not found'

  return Response(response=response_text,
                  content_type='text/plain;charset=utf-8')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
