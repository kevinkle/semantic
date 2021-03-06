#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Classes:
	Contig: a sequence of DNA that belongs to a Genome
"""

from named_individual import *
from superphy.upload import _sparql

class Contig(NamedIndividual):
    """
    A contig and its associated informatics metadata.
    """

    def __init__(self, graph, name, genome, sequence, is_from):
        """
        Create a Contig with its associated metadata.
        Args:
            graph(rdflib.Graph): container object to store RDF triples
            name (str): name of the contig (its accession number)
            genome (str): the genome that the contig belongs to
            sequence (str): the contig's sequence
            is_from (str): identifier explaining origin of sequence (e.g. WGS, PLASMID, CORE)
        """
        super(Contig, self).__init__(graph, name)
        self.genome = genome
        self.sequence = sequence
        self.is_from = is_from


    def rdf(self):
        """
        Convert all Sequence variables to RDF and adds it to the graph
        """

        super(Contig, self).rdf()
        self.graph.add((n[self.name], rdf.type, gfvo.Contig))

        self.graph.add((n[self.name], n.has_sequence, Literal(str(self.sequence), datatype=XSD.string)))
        self.graph.add((n[self.name], n.is_from, Literal(str(self.is_from), datatype=XSD.string)))
        self.graph.add((n[self.genome], n.has_contig, n[self.name]))
        self.graph.add((n[self.name], n.is_contig_of, n[self.genome]))


    def add_seq_validation(self, boolean):
        """
        Converts result of sequence validation to RDF and adds it to the graph
        Args:
            boolean (bool): indicates whether or not the sequence has passed validation
        """
        self.graph.add((n[self.name], n.has_valid_sequence, Literal(str(boolean), datatype=XSD.string)))

        if not _sparql.check_validation(self.genome):
            self.graph.add((n[self.genome], n.has_valid_sequence, Literal(str(boolean), datatype=XSD.string)))
        
