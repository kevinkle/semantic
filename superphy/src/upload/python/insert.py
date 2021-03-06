#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#use: python insert.py -i samples/ANLJ01.1.fsa_nt

import logging

from _utils import generate_output, generate_uri as gu, upload_data

def generate_graph():
    '''
    Parses all the Namespaces defined in the config file and returns a graph
    with them bound.

    Return:
        (rdflib.Graph): a graph with all the defined Namespaces bound to it.
    '''
    import settings

    from rdflib import Namespace, Graph

    graph = Graph()

    for key in settings.namespaces.keys():
        if key is 'root':
            graph.bind('', settings.namespaces['root'])
        else:
            graph.bind(key, settings.namespaces[key])

    return graph

def parse_nih_name(description):
    """
    Parses a String of a nih name (eg. record.description after Bio.SeqIO.parse)
    and returns a dictionary of the substrings we're interesting FOR creating
    uriSpecies

    Args:
        description (str): a record.description
        ex. gi|427200135|gb|ANLJ01000508.1| Escherichia coli 89.0511 gec890511.contig.603_1, whole genome shotgun sequence
    Returns:
        (dict) with keys: accession_id, species, assembly, contig
        ex. {'accession_id': 'ANLJ01000508', 'contig': '000508', 'assembly': 'ANLJ01', 'species': '89.0511'}

    TODO:
        -add code to parse other nih naming conventions
        -what happens when no species name??
    """
    if '|' in description:
        #of format: >gi|427220012|gb|ANLJ01000001.1| Escherichia coli 89.0511 gec890511.contig.0_1, whole genome shotgun sequence
        identifiers = {'accession_id' : description.split("|")[3].split(".")[0]} # ANLJ01000001.1
        identifiers['species'] = description.split("|")[4].split(" ")[3] # 89.0511
        identifiers['assembly'] = identifiers['accession_id'][0:6] # ANLJ01
        identifiers['contig'] = identifiers['accession_id'][6:12] # 000001.1
    elif description[0].isalpha() and description[1].isalpha() and description[2].isdigit() and '.contig.' in description:
        #of format: JH709084.1 Escherichia coli PA10 genomic scaffold PA10.contig.633, whole genome shotgun sequence
        identifiers = {'accession_id' : description.split(" ")[0]}
        identifiers['species'] = description.split('.contig.')[0].split(' ')[-1]
        identifiers['assembly'] = identifiers['species'] #this differs from the other 2 cases, here the assembly is just the strain of e.coli because each contig has a unique accession #
        identifiers['contig'] = description.split('.contig.')[1].split(' ')[0]
    else:
        #assuming: >AJMD01000001.1 Escherichia coli NCCP15658 NCCP15658_contig01, whole genome shotgun sequence
        identifiers = {'accession_id' : description.split(" ")[0]} # AJMD01000001.1
        identifiers['species'] = description.split('coli ')[1].split(' ')[0] # NCCP15658
        identifiers['assembly'] = identifiers['accession_id'][0:6] # AJMD01
        identifiers['contig'] = identifiers['accession_id'][6:12] # 000001.1
    return identifiers

def generate_turtle(graph, fasta_file, uriIsolate):
    '''
    Handles the main generation of a turtle object.

    Args:
        graph(rdflib.Graph): the graph instance that is 1:1 with a .fasta file
        fasta_file(str): path to the .fasta file (this should incl the directory)
        spfyID(hash): a hash value generated from the name of the fasta file
    Returns:
        graph: the graph with all the triples generated from the .fasta file

    TODO:
    -make a check against the db so spfyID is unique to particular isolates
    '''

    from Bio import SeqIO
    from rdflib import Literal

    graph.add((uriIsolate, gu('rdf:type'), gu('ncbi:562'))) #rdflib.Namespace seems to not like numbers hence ge + '0001567'
    graph.add((uriIsolate, gu('ge:0001567'), Literal("bacterium"))) #rdflib.Namespace seems to not like numbers hence ge + '0001567'

    for record in SeqIO.parse(open(fasta_file), "fasta"):
        identifiers = parse_nih_name(record.description)

        #creating :spfy1/ANLJ01
        #this is repetitive for the same assembly
        #uriAssembly = gu(uriIsolate, '/' + identifiers['assembly'])
        #TODO: add in ECTyper so we can get unique ids for isolates, hash of filename maybe ideal for assemblies or just use filename
        uriAssembly = gu(uriIsolate, '/' + str(hash(fasta_file.split('/')[-1]))) #done to ensure 1:1 for now
        #associatting isolate URI with assembly URI
        graph.add((uriIsolate, gu('g:Genome'), uriAssembly))
        graph.add((uriIsolate, gu('g:Name'), Literal('Escherichia coli' + identifiers['species'])))

        #the assembly aka the genome (kindof)
        #no longer using blank node, instead uri for bag of contigs
        uriContigs = gu(uriAssembly + "/contigs")
        graph.add((uriAssembly, gu('so:0001462'), uriContigs))
        if '/' in fasta_file: #check for path incl
            graph.add((uriAssembly, gu('dc:source'), Literal(fasta_file.split('/')[-1])))
        else:
            graph.add((uriAssembly, gu('dc:source'), Literal(fasta_file)))
        graph.add((uriAssembly, gu('dc:description'), Literal(record.description)))

        #creating :spfy1/ANLJ01/00001.1 ie. the contig uri
        uriContig = gu(uriAssembly, '/' + identifiers['contig'])
        graph.add((uriContigs, gu('g:Contig'), uriContig))
        graph.add((uriContig, gu('g:DNASequence'), Literal(record.seq)))
        graph.add((uriContig, gu('dc:source'), Literal(identifiers['accession_id'])))

    return graph

def call_ectyper(graph, fasta_file, uriIsolate):
    #i don't intend to import anything from ECTyper (there are a lot of imports in it - not sure if we'll use them all)
    import subprocess

    from rdflib import Literal
    from ast import literal_eval
    from os.path import splitext

    logging.info('calling ectyper from fun call_ectyper')
    #concurrency is handled at the batch level, not here (note: this might change)
    #we only use ectyper for serotyping, amr is handled by rgi directly
    ectyper_dict = subprocess.check_output(['./ecoli_serotyping/src/Tools_Controller/tools_controller.py',
        '-in', fasta_file,
        '-s', '1'
        ])
    logging.info('inner call completed')

    #because we are using check_output, this catches any print messages from tools_controller
    #TODO: switch to pipes
    if 'error' in ectyper_dict.lower():
        logging.error('ectyper failed for' + fasta_file)
        print 'ECTyper failed for: ', fasta_file
        print 'returning graph w/o serotype'
        return graph

    logging.info('evalulating ectyper output')
    #generating the dict
    ectyper_dict = literal_eval(ectyper_dict)
    logging.info('evaluation okay')

    #we are calling tools_controller on only one file, so grab that dict
    ectyper_dict = ectyper_dict[splitext(fasta_file)[0].split('/')[-1]]

    #serotype parsing
    graph = parse_serotype(graph, ectyper_dict['Serotype'], uriIsolate)
    logging.info('serotype parsed okay')

    #amr
    graph = generate_amr(graph, uriIsolate, fasta_file)


    return graph

def parse_serotype(graph, serotyper_dict, uriIsolate):
    if 'O type' in serotyper_dict:
        graph.add((uriIsolate, gu('ge:0001076'), Literal(serotyper_dict['O type'])))
    if 'H type' in serotyper_dict:
        graph.add((uriIsolate, gu('ge:0001077'), Literal(serotyper_dict['H type'])))
    if 'K type' in serotyper_dict:
        graph.add((uriIsolate, gu('ge:0001684'), Literal(serotyper_dict['K type'])))

    return graph

def generate_amr(graph, uriIsolate, fasta_file):
    import subprocess
    import pandas

    from os import rename

    if '/' in fasta_file:
        outputname = fasta_file.split('/')[-1]
    else:
        outputname = fasta_file

    #differs from ectyper as we dont care about the temp results, just the final .tsv
    #direct (the main) call
    subprocess.call(['rgi',
        '-i', fasta_file,
        '-o', 'outputs/' + outputname])

    #the rgi_json call in rgitool.py isn't needed for us
    #this generates the .tsv we want
    subprocess.call(['rgi_jsontab',
        '-i', 'outputs/' + outputname + '.json',
        '-o', 'outputs/' + outputname])

    rename('outputs/' + outputname + '.txt', 'outputs/' + outputname + '.tsv')

    amr_results = pandas.read_table('outputs/' + outputname + '.tsv')

    return graph

if __name__ == "__main__":

    import argparse
    import os #for batch cleanup

    from Bio import SeqIO
    from rdflib import Namespace, BNode, Graph, URIRef, Literal
    from ConfigParser import SafeConfigParser

    #setting up graph
    graph = generate_graph()

    #parsing cli-input
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help = "FASTA file",
        required = True
    )
    args = parser.parse_args()

    #starting logging
    logging.basicConfig(
        filename = 'outputs/' + __name__ + args.i.split('/')[-1] + '.log',
        level = logging.INFO
    )

    print("Importing FASTA from: " + args.i)
    logging.info('importing from' + args.i)

    #we do this outside of record as we want same uri for all isolates
    #todo: add some check if same fasta files represents same isolate
    #grabs current id #
    #TODO: replace ID with query to sparql endpoint to check / maybe base of serotype
    spfyID = hash(args.i.split('/')[-1]) #just from the filename (not incl the dir)

    #makes the spfy uri -> currently unique to a file
    #TODO: do check to make unique to an isolate
    uriIsolate = gu(':spfy' + str(spfyID))

    logging.info('generating barebones ttl from file')
    graph = generate_turtle(graph, args.i, uriIsolate)
    logging.info('barebones ttl generated')

    logging.info('calling ectyper')
    graph = call_ectyper(graph, args.i, uriIsolate)
    logging.info('ectyper call completed')

    print "Uploading to Blazegraph"
    logging.info('uploading to blazegraph')
    confirm = upload_data(generate_output(graph))
    print confirm
    logging.info(confirm)
    print 'uploaded wooot!'

    #removing fasta
    #os.remove(args.i)
    os.remove('outputs/' + __name__ + args.i.split('/')[-1] + '.log')
