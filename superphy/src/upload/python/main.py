#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
A module used to initialize and set up the superphy namespace in Blazegraph
"""

import gc

from superphy.upload import _sparql
from superphy.upload.blazegraph_upload import BlazegraphUploader
from superphy.upload.blazegraph_setup import BlazegraphSetup

__author__ = "Stephen Kan"
__copyright__ = """
    © Copyright Government of Canada 2012-2015. Funded by the Government of
    Canada Genomics Research and Development Initiative"""
__license__ = "ASL"
__version__ = "2.0"
__maintainer__ = "Stephen Kan"
__email__ = "stebokan@gmail.com"

#response = BlazegraphUploader().create_namespace()

def init():
    """
    .
    """
    BlazegraphSetup().setup_curated_data()
    BlazegraphUploader().upload_all_ontologies()
    gc.collect()
    _sparql.delete_blank_nodes()
