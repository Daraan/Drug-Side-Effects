from typing import List, Union

import rdflib
# just some listings, check what we need
import rdflib.namespace
import rdflib.plugins.sparql
import rdflib.plugins.sparql.parser
import rdflib.plugins.sparql.sparql
from rdflib.plugins.sparql.processor import SPARQLResult

from rdflib import Graph
import owlrl

import query_strings
import preprocessing as pre

from pyparsing.exceptions import ParseException

import time

# Prepared queries for frontend

# also read: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html#prepared-queries

import pandas as pd

from operator import methodcaller, itemgetter

toPython = methodcaller(
    "toPython")  # converts results to python objects, e.g. not as URI objects

DEBUG = False


class KnowledgeBase:

  def __init__(self, *sources):
    # TODO: Add NamespaceManager !!!!
    self.graph: Graph = Graph()
    for source in sources:
      print("parsing", source)
      self.parse(source, format="turtle")
    print("done")

  def parse(self, s, *args, **kwargs):
    start = time.time()
    try:
      return self.graph.parse(s, *args, **kwargs)
    except ParseException:
      print(s)
      raise
    finally:
      end = time.time()
      if end - start > 60:
        print("Parsing took: ", end - start, "seconds")

  def query(self, s, *args, **kwargs):
    start = time.time()
    if DEBUG:
      print(s)  # set to true to print
    try:
      return self.graph.query(s, *args, **kwargs)
    except ParseException:
      print(s)
      raise
    finally:
      end = time.time()
      if end - start > 60:
        print("Query took: ", end - start, "seconds")

  def sideffect_single_drug(self, stitch_id):
    s = query_strings.sideeffect_single_drug(stitch_id)
    results = self.query(s)  # initBindings={"stitch_id": stitch_id}
    return results

  def sideffect_drug_drug(self, id1, id2):
    """
        Returns the side-effects of the drug-drug-combination but not the side-effects
        of the individual drugs.
        """
    s = query_strings.sideeffect_drug_drug(id1, id2)
    results = list(self.query(s))
    for r in results:
      print(r)
    return results

  # def side_effects_drug_list(self, *stitch_ids):
  #   results: List[rdflib.query.Result] = []
  #   stitch_ids = list(stitch_ids)
  #   while len(stitch_ids) > 1:
  #     stitch_id = stitch_ids.pop()
  #     s = query_strings.drug_side_effect_and_interactions(
  #         stitch_id, *stitch_ids)
  #     result: rdflib.query.Result = self.query(s)
  #     results.extend(result)
  #   #NOTE: TODO: Below works, uncomment when above works too,
  #   results.extend(self.sideffect_single_drug(
  #       stitch_ids.pop()))  # nore more interactions
  #   return results

  def side_effects_drug_list(self, *stitch_ids):
    results: List[rdflib.query.Result] = []
    stitch_ids = list(stitch_ids)

    while len(stitch_ids) > 1:
      stitch_id = stitch_ids.pop()
      if not stitch_ids:  # Check if the list is empty after popping
        break  # Exit the loop if the list is empty
      s = query_strings.drug_side_effect_and_interactions(
          stitch_id, *stitch_ids)
      result: rdflib.query.Result = self.query(s)
      results.extend(result)

    if stitch_ids:  # Check if there's still an element in the list
      results.extend(self.sideffect_single_drug(stitch_ids.pop()))

    return results

  def side_effects_of_drug_names(self, *drug_names):
    s1 = query_strings.names_to_stitch(*drug_names)
    stitch_results = self.query(s1)
    # ids = list(r[0].split("/")[-1] for r in stitch_results)
    ids = [str(r[0]).split("/")[-1] for r in stitch_results]
    print("Found stitch ids: ", ids)
    return self.side_effects_drug_list(*ids)

  def all_from_names(self, *drug_names):
    s = query_strings.all_from_names(*drug_names)
    return self.query(s)

  def get_all_drugs(self):
    result = self.query("""
        SELECT ?stitch_id
        WHERE
        { ?stitch_id a sider:Drug}
        """)
    return [r[0].toPython() for r in result]

  # TODO: this should be more streightforward -> a single dict.
  KEYS = ["side_effect_source", "side_effect_code",
          "side_effect_term"]  #MUST MATCH QUERIES
  KEY_MAPPINGS = dict.fromkeys(KEYS)
  KEY_MAPPINGS["side_effect_source"] = "Side Effect Source"
  KEY_MAPPINGS["side_effect_code"] = "Side Effect Code"
  KEY_MAPPINGS["side_effect_term"] = "Side Effect Term"

  def result_to_df(
      self, result: Union[SPARQLResult, List[SPARQLResult]]) -> pd.DataFrame:
    if not isinstance(result, rdflib.query.ResultRow) and isinstance(
        result, (list, tuple)):
      return pd.concat([self.result_to_df(r) for r in result if len(r) > 0])
    try:
      if isinstance(result, rdflib.query.ResultRow):
        return pd.DataFrame(
            [[toPython(result[k]) for k in self.KEYS]],
            columns=[self.KEY_MAPPINGS[str(c)] for c in self.KEYS])
      return pd.DataFrame(
          [[toPython(r[k]) for k in self.KEYS] for r in result],
          columns=[self.KEY_MAPPINGS[str(c)] for c in self.KEYS])
    except ValueError:
      print([toPython(result[k]) for k in self.KEYS])
      raise
    except TypeError:
      print("result is", result, type(result))

      raise

  def result_to_html(self, result: Union[SPARQLResult, List[SPARQLResult]],
                     **kwargs):
    df = self.result_to_df(result)
    return df.to_html(**kwargs)


if __name__ == "__main__":
  from importlib import reload
  import query_strings as qs
  import kg_backend
  kb = kg_backend.KnowledgeBase("files/SEQT-Onthology.ttl",
                                "files/SNAP-A-Box_test.ttl")
  r = kb.query(
      qs.PREFIXE +
      """SELECT ?d WHERE {VALUES ?a { :CID003062316} . ?a  sider:side-effect ?c . ?c sider:preferred-term ?d }"""
  )
  list(r)
