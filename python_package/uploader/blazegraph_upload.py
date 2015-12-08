#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Module containing some utility functions to upload data and files of various formats ont Blazegraph
"""

import os

import requests

from _utils import generate_path

__author__ = "Stephen Kan"
__copyright__ = "© Copyright Government of Canada 2012-2015. Funded by the Government of Canada Genomics Research and Development Initiative"
__license__ = "ASL"
__version__ = "2.0"
__maintainer__ = "Stephen Kan"
__email__ = "stebokan@gmail.com"

class BlazegraphUploader(object):
    """
    A class that sets up data upload to Blazegraph via the initialized specified namespace
    """

    bg_url = "http://localhost:9999/bigdata/namespace/superphy/sparql"

    def __init__(self):
        pass

    def upload_all_ontologies(self):
        """
        Uploads all ontologies in the specified folder.

        The format of the ontology is automatically interpreted by Blazegraph based on the file extension. If any
        format fails, it is probably because of an extension mismatch (for example, Turtle files are not .owl as the
        WC3 standardized file format for RDF and OWL is RDF/XML.

        """
        folder = generate_path("ontologies")
        files = os.listdir(folder)

        for file in files:
            ontology = os.path.join(folder, file)
            self.upload_file(ontology)

    def upload_file(self, filepath):
        """
        Upload a specified file onto Blazegraph.

        The format of the file is automatically interpreted by Blazegraph based on the file extension. If any
        format fails, it is probably because of an extension mismatch (for example, Turtle files are not .owl as the
        WC3 standardized file format for RDF and OWL is RDF/XML.

        Args:
            filepath (str): relative filepath from this python script

        Prints out the response object from Blazegraph

        """
        file = "file:" + filepath
        data = {'uri': file}
        r = requests.post(self.bg_url, data)
        print r.content

    def upload_data(self, data):
        """Uploads raw data onto Blazegraph. To ensure that Blazegraph interprets properly, it is necessary to specify
        the format in a Context-Header.

        Accepted formats are listed on this site: https://wiki.blazegraph.com/wiki/index.php/REST_API#MIME_Types

        Currently, the only data type needed is turtle, so this function is not usable for other formats.

        Args:
            data (turtle): a turtle data object

        Prints out the response object from Blazegraph
        """
        headers = {'Content-Type':'application/x-turtle'}
        r = requests.post(self.bg_url, data=data, headers=headers)
        print r.content

    def create_namespace(self):
        """
        Creates the superphy namespace based on the options in data/namespace.xml

        Returns: the response object from superphy used for control flow

        """
        headers = {'Content-Type':'application/xml'}
        data = "".join(line for line in open(generate_path("data/namespace.xml")))
        r = requests.post('http://localhost:9999/bigdata/namespace', data=data, headers=headers)
        return r.content