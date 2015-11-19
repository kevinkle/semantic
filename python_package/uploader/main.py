__author__ = 'Stephen Kan'

from ontology_uploader import upload_all_ontologies, create_namespace
from blazegraph_setup import generate_all
import gc
import _sparql

response = create_namespace()

if ("EXISTS" in response):
    print response
else:
    print response
    generate_all()
    upload_all_ontologies()
    gc.collect()
    _sparql.delete_blank_nodes()