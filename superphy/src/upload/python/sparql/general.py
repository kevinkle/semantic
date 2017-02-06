#!/usr/bin/python
#Filename: general_query_strings.py
#Author: Bryce Drew
#Date: Sept. 30, 2015
#Functionality:
    #These are sparql queries. They are designed to be general non-specific queries:

from sparql.endpoint import Endpoint

def delete_all_triples():
    Endpoint.update("""DELETE {?s?p?o} WHERE {?s?p?o}""")

#The sparql statement will get all triples
def get_all_triples(): #Verified
    return Endpoint.query("""SELECT * {?s ?p ?o}""")

#The sparql statement will get all triples with object literals
def get_object_literals(): #Verified
    return Endpoint.query("""SELECT ?s ?p ?o WHERE {?s ?p ?o FILTER  ISLITERAL(?o)}""")

def get_x_triples(x):
    return Endpoint.query("""SELECT * {?s ?p ?o} LIMIT %s""" % (x))

#The sparql statement will get all tripples with at least 1 literal
def get_all_literals():
    return Endpoint.query("""
    SELECT ?s ?p ?o
    WHERE {
      {?s ?p ?o
       FILTER  ISLITERAL(?o)
      }
      UNION
      {?s ?p ?o
       FILTER  ISLITERAL(?p)
      }
      UNION
      {?s ?p ?o
       FILTER  ISLITERAL(?s)
      }
    }""")

#Tested
#The sparql statement will get all triples with 3 URIs.
def get_all_uri_triples():
    return Endpoint.query("""
    SELECT ?s ?p ?o
    WHERE {
      {?s ?p ?o}
      MINUS
      {?s ?p ?o
        FILTER ISLITERAL(?o)
      }
      MINUS
      {
        FILTER ISLITERAL(?p)
      }
      MINUS
      {
        FILTER ISLITERAL(?s)
      }
    }""")
