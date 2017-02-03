import logging
import time

# Redis Queue
from redis import Redis
from rq import Queue

# other libraries for rdflib
from rdflib import Graph

# our own slightly more general stuff
from insert import insert
from turtle_grapher import generate_output
from turtle_utils import generate_uri as gu

# for various features we add
from savvy import savvy  # serotype/amr/vf


def spfy(args_dict):
    '''
    # note: the timeout times refer to how long the job has once it has STARTED executing
    # we use the high priority queue for things that should be immediately returned to the user
    high = Queue('high', default_timeout=80)  # 80 seconds
    low = Queue('low', default_timeout=600)
    '''

    # use 1 queue for now
    high = Queue('high', connection=Redis())

    loggging.info('Starting savvy call...')
    sav = high.enqueue(savvy, args_dict)
    logging.info(sav.id)
    time.sleep(180)
    graph = sav.result

    logging.info('uploading to blazegraph')
    print "Uploading to Blazegraph"
    print insert(graph)
    print 'uploaded wooot!'


if __name__ == "__main__":
    import argparse
    import os  # for batch cleanup

    from ConfigParser import SafeConfigParser
    from turtle_utils import generate_hash

    # parsing cli-input
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="FASTA file",
        required=True
    )
    parser.add_argument(
        "--disable-serotype",
        help="Disables use of the Serotyper. Serotyper is triggered by default.",
        action="store_true"
    )
    parser.add_argument(
        "--disable-vf",
        help="Disables use of ECTyper to get associated Virulence Factors. VFs are computed by default.",
        action="store_true"
    )
    parser.add_argument(
        "--disable-amr",
        help="Disables use of RGI to get Antimicrobial Resistance Factors.  AMR genes are computed by default.",
        action="store_true"
    )
    # note: by in large, we expect uri to be given as just the unique string
    # value  (be it the hash or the integer) without any prefixes, the actual
    # rdflib.URIRef object will be generated in this script
    # this is mainly for batch computation
    parser.add_argument(
        "--uriGenome",
        help="Allows the specification of the Genome URI separately. Expect just the hash (not an actual uri).",
    )
    # This is both for batch computation and for future extensions where there
    # are multiple sequencings per isolate (Campy)
    parser.add_argument(
        "--uriIsolate",
        help="Allows the specification of the Isolate URI separately. Expect just the integer (not the full :spfyID)",
        type=int
    )
    args = parser.parse_args()
    # we make a dictionary from the cli-inputs and add are uris to it
    # mainly used for when a func needs a lot of the args
    args_dict = vars(args)

    # starting logging
    logging.basicConfig(
        filename='outputs/' + __name__ +
        args_dict['i'].split('/')[-1] + '.log',
        level=logging.INFO
    )

    # check if a genome uri isn't set yet
    if args_dict['uriIsolate'] is None:
        # this is temporary, TODO: include a spqarql query to the db
        uriIsolate = gu(':spfy' + str(hash(args_dict['i'].split('/')[-1])))
    else:
        uriIsolate = gu(':spfy' + args_dict['uriIsolate'])

    # if the fasta_file hash was not precomputed (batch scripts should
    # precompute it), we compute that now
    if args_dict['uriGenome'] is None:
        uriGenome = gu(':' + generate_hash(args_dict['i']))
    else:
        uriGenome = gu(':' + args_dict['uriGenome'])

    args_dict['uriIsolate'] = uriIsolate
    args_dict['uriGenome'] = uriGenome

    spfy(args_dict)
