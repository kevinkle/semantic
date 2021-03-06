#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from named_individual import *
from superphy.upload import _sparql

class Gene(NamedIndividual):
    """
    A gene with associated metadata

    """

    def __init__(self, graph, name, **kwargs):
        """
        Creates a Gene with associated metadata

        **kwargs is a dictionary of optional metadata used to pass them in

        Attributes:
            searchparam: list of keywords to filter kwargs by

        Args:
            graph (rdflib.Graph): container object to store RDF triples
            name (str): name of the Gene
            **kwargs (dict): optional arguments for Gene, that will be filtered for
                           spurious entries

        """
        searchparam = ["gene",
                       "category", 
                       "subcategory",
                       "vfo_id",
                       "uniprot",
                       "gene_type",
                       "aro_id", 
                       "aro_accession"]

        super(Gene, self).__init__(graph, name)
        self.kwargs = {key: value for key, value in kwargs.items() if key in searchparam}


    def rdf(self):
        """
        Convert all Gene metadata to RDF and adds it to the graph

        As methods are called based on their keys, there is some coupling with minerJSON.py to
        ensure that the keys are properly named.
        """

        super(Gene, self).rdf()

        for key, value in self.kwargs.iteritems():
            getattr(self, key)(value)

        self.graph.add((n[self.name], rdf.type, gfvo.gene))


    def gene(self, gene):
        """
        Converts gene name literal to RDF and adds it to graph
        """

        gene_literal, = gene

        literal = Literal(gene_literal, datatype=XSD.string)
        self.graph.add((n[self.name], n.has_name, literal))


    def vfo_id(self, vfo_id):
        """
        Converts VFO ID into RDF and adds it to the graph

        Args:
            vfo_id(str): an id from VFDB
        """
        v_id, = vfo_id

        literal = Literal(v_id, datatype=XSD.string)
        self.graph.add((n[self.name], n.has_vfo_id, literal))

    def category(self, categories):
        """
        Converts the category to RDF and adds it to the graph

        Args:
            categories(str): list of categories that the gene belongs to
        """

        for item in categories:
            literal = Literal(item, datatype=XSD.string)
            self.graph.add((n[self.name], n.has_category, literal))

    def subcategory(self, subcategories):
        """
        Converts all sub categories into RDF and adds it to the graph

        Args:
            sub_categories: list of sub categories that the gene belongs to
        """

        for item in subcategories:
            literal = Literal(item, datatype=XSD.string)
            self.graph.add((n[self.name], n.has_sub_category, literal))

    def uniprot(self, uniprot):
        """
        Converts Uniprot into RDF and adds it to the graph

        Args:
            uniprot(str): a Uniprot ID
        """

        uni, = uniprot
        uniprots = uni.split(",")

        literal = Literal(uniprots[0], datatype=XSD.string)
        self.graph.add((n[self.name], n.has_uniprot, literal))

    def gene_type(self, gene_type):
        """
        Adds the type of the gene to the graph.

        Args:
            gene_type(string): string describing the type of gene (e.g. virulence factor)
        """
        g_type, = gene_type

        self.graph.add((n[self.name], rdf.type, n[g_type]))

    def aro_accession(self, aro_accession):

        accession, = aro_accession

        literal = Literal(accession, datatype=XSD.string)
        self.graph.add((n[self.name], n.has_aro_accession, literal))

    def aro_id(self, aro_id):

        aroid, = aro_id

        literal = Literal(aroid, datatype=XSD.string)
        self.graph.add((n[self.name], n.has_aro_id, literal))



class GeneLocation(NamedIndividual):
    """
    A class for information about a gene and its location on a contig.
    """

    def __init__(self, graph, name, gene, contig, begin, end, seq, is_ref_gene, cutoff):
        """
        Creates a GeneLocation with beginning and end positions using the faldo ontology

        Args:
            graph (rdflib.Graph): container object to store RDF triples
            name (str): gene name  + "_" + contig name + occurence number
            gene (str): the name of the gene
            contig (str): name of the contig its found in
            begin (str): the beginning position of the gene in contig
            end (str): the end position of the gene in contig
            seq (str): the sequence of the gene on the contig
            is_ref_gene (boolean): signifies whether this is the reference gene location for a particular gene
            cutoff(str): from RGI analysis for AMR, one of Loose, Perfect or Strict

        """

        super(GeneLocation, self).__init__(graph, name)
        self.gene = gene
        self.contig = contig
        self.begin = begin
        self.end = end
        self.seq = seq
        self.is_ref_gene = is_ref_gene
        self.cutoff = cutoff


    def rdf(self):
        """
        Converts all parameters into RDF and adds it to the graph
        """

        super(GeneLocation, self).rdf()
        self.graph.add((n[self.name], rdf.type, faldo.Region))
        self.graph.add((n[self.gene], n.has_copy, n[self.name]))
        self.graph.add((n[self.gene], rdf.type, gfvo.gene))
        self.graph.add((n[self.name], n.references, n[self.contig]))
        self.graph.add((n[self.contig], n.has_gene, n[self.name]))
        self.graph.add((n[self.name], n.is_gene_of, n[self.contig]))
        if self.cutoff:
            self.graph.add((n[self.name], n.type_match, n[self.cutoff]))

        if self.is_ref_gene:
            self.graph.add((n[self.name], rdf.type, n.reference_gene))
            self.graph.add((n[self.gene], n.has_reference_gene, n[self.name]))

        # begin
        literal = Literal(self.begin, datatype=XSD.string)
        begin_name = self.name + "_begin"
        self.graph.add((n[self.name], faldo.begin, n[begin_name]))
        self.graph.add((n[begin_name], rdf.type, faldo.Position))
        self.graph.add((n[begin_name], rdf.type, faldo.ExactPosition))
        self.graph.add((n[begin_name], rdf.type, faldo.ForwardStrandPosition))
        self.graph.add((n[begin_name], faldo.position, literal))
        self.graph.add((n[begin_name], faldo.reference, n[self.contig]))

        # end
        literal = Literal(self.end, datatype=XSD.string)
        end_name = self.name + "_end"
        self.graph.add((n[self.name], faldo.end, n[end_name]))
        self.graph.add((n[end_name], rdf.type, faldo.Position))
        self.graph.add((n[end_name], rdf.type, faldo.ExactPosition))
        self.graph.add((n[end_name], rdf.type, faldo.ForwardStrandPosition))
        self.graph.add((n[end_name], faldo.position, literal))
        self.graph.add((n[end_name], faldo.reference, n[self.contig]))

        # sequence
        literal = Literal(self.seq, datatype=XSD.string)
        self.graph.add((n[self.name], n.has_sequence, literal))
