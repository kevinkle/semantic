#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
A module containing some generic utility functions for the project

"""

import inspect
import os
import string

def generate_path(filename):
    """
    Generates the absolute filepath based on the location of the caller of this
    function

    Args:
        filename (str): relative location of the caller

    Returns: absolute filepath for the given filename based on the location of
    the caller

    """
    frame = inspect.stack()
    (frame, filepath, line_number, function_name, lines, index) = frame[1]
    del frame
    return os.path.join(os.path.dirname(filepath), filename)

def strip_non_alphabetic(str_):
    """
    Strips all non-alphabetic characters (not present in string.ascii_letters)
    from a given string

    Args:
        str: any string

    Returns: a string with only characters from string.ascii_letters

    """
    all_ = string.maketrans('', '')
    nochars = all_.translate(all_, string.ascii_letters)
    return str_.translate(all_, nochars)

def strip_non_numeric(str_):
    """
    Strips all non-numeric characters (not present in string.digits) from a
    given string

    Args:
        str: any string

    Returns: a string with only characters from string.digits

    """
    all_ = string.maketrans('', '')
    nodigs = all_.translate(all_, string.digits)
    return str_.translate(all_, nodigs)

def generate_output(graph):
    """
    Returns RDF Graph data in the turtle format and clears the Graph

    Args:
        graph (rdflib.Graph): container object to store RDF triples
    """

    output = graph.serialize(format="turtle")
    return output

def generate_file_output(graph, destination):
    """
    Export RDF Graph data to a turtle file at the given destination

    Args:
        graph (rdflib.Graph): container object to store RDF triples
        destination (str): an internal filepath relative to the  __init__.py
        file this module belongs to
    """

    graph.serialize(destination=destination, format="turtle")

def generate_uri(uri, s=''):
    """
    Takes a string as one would define for .ttl files and returns a URI for rdflib.

    Args:
        uri (str): a string following .ttl convention for a URI
        ex. g:Identifier as shorthand for http://www.biointerchange.org/gfvo#Identifier
    Returns:
        (rdflib.URIRef) with URI needed to add to rdflib.Graph
    """
    import settings #this is the settings.py

    from rdflib import Namespace, URIRef, Literal

    #if you call with a uri already
    if isinstance(uri, URIRef):
        return URIRef(str(uri) + s)

    prefix = uri.split(':')[0]
    postfix = uri.split(':')[1]

    if prefix == '': #this is our : case
        return URIRef(settings.namespaces['root'] + postfix)
    else:
        return URIRef(settings.namespaces[prefix] + postfix)

def from_nuccore(accession):
    """Obtains the FASTA sequence via the NCBI Genbank Nucleotide database
    using Entrez EUtils. If found writes it the tmp/ folder and turns the path of the file.
    If there is nothing found for the sequence, raise a ValueError.

    Args:
        accession (str): genbank accession id
    Returns:
        (str) containing the path of the downloaded *.fasta file
    """

    from Bio import Entrez, SeqIO

    Entrez.email = "superphy.info@gmail.com"
    handle = None
    i = 0

    while i < 3:
        try:
            handle = Entrez.efetch(
                db="nuccore",
                id=accession,
                rettype="fasta",
                retmode="text"
            )
            if not handle is None:
                SeqIO.write(handle, 'tmp/' + accession + '.fasta', 'fasta')
                return 'tmp/' + accession + '.fasta'
        except:
            i += 1
            continue
    try:
        handle is None
    except NameError:
        raise TypeError("Could not retrieve file for analysis")

def download_fasta(url):
    """Downloads the gzip file with the correct id and filetype and unzips
    it and transfers its contents into a temporary FASTA file for further
    processing. Removes the gzipped file.

    Args:
        url(str): the full url for the file
        ex. ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA_900148645.1_Hp_23-13_05/GCA_900148645.1_Hp_23-13_05_genomic.fna.gz
    Return:
        (str): Path of the unzipped .fasta file
    """
    import gzip, os

    from time import sleep
    from urllib import urlretrieve

    sleep(1) #so it doesn't boot us off

    filename = 'tmp/' + url.split('/')[-1]
    print 'filename is ' + filename
    urlretrieve(url, filename)

    with gzip.open(filename) as fasta, \
        open(filename.strip('.gz'), 'wb') as output:
        output.write(fasta.read())
        print 'wrote file!'
    os.remove(filename)

    return filename.strip('.gz')

def upload_data(data):
    """
    Uploads raw data onto Blazegraph. To ensure that Blazegraph interprets
    properly, it is necessary to specify the format in a Context-Header.

    Accepted formats are listed on this site:
    https://wiki.blazegraph.com/wiki/index.php/REST_API#MIME_Types

    Currently, the only data type needed is turtle, so this function is not
    usable for other formats.

    Args:
        data (turtle): a turtle data object

    Prints out the response object from Blazegraph
    """

    import requests, os
    import settings

    url = settings.database['blazegraph_url']

    headers = {'Content-Type':'application/x-turtle'}
    request = requests.post(
        os.getenv(
            'SUPERPHY_RDF_URL',
            url
        ),
        data=data,
        headers=headers
    )
    return request.content
