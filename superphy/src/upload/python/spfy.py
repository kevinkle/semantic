import logging
import time
import os

# Redis Queue
from redis import Redis
from rq import Queue
# for details, see: https://github.com/nvie/rq/pull/421
from rq.registry import FinishedJobRegistry, StartedJobRegistry
# details:
    # https://realpython.com/blog/python/flask-by-example-implementing-a-redis-task-queue/
    # http://stackoverflow.com/questions/15181630/how-to-get-job-by-id-in-rq-python
from rq.job import Job

# other libraries for rdflib
from rdflib import Graph

# our own slightly more general stuff
from insert import insert
from turtle_grapher import generate_output
from turtle_utils import generate_uri as gu, generate_hash

# for various features we add
from savvy import savvy  # serotype/amr/vf

# the only ONE time for global variables
# when naming queues, make sure you actually set a worker to listen to that queue
# we use the high priority queue for things that should be immediately
# returned to the user
redis_conn = Redis()
high = Queue(connection=redis_conn)
low = Queue('low', connection=redis_conn, default_timeout=600)


def blob_savvy(args_dict):
    '''
    Handles savvy.py's pipeline.
    '''
    if os.path.isdir(args_dict['i']):
        for f in os.listdir(args_dict['i']):
            single_dict = dict(args_dict.items() + {'uriIsolate': args_dict['uris'][f][
                               'uriIsolate'], 'uriGenome': args_dict['uris'][f]['uriGenome'], 'i': args_dict[i] + '/' + f}.items())
            high.enqueue(savvy, dict(single_dict.items() +
                                     {'disable_amr': True}.items()))
            low.enqueue(savvy, dict(single_dict.items() +
                                    {'disable_vf': True, 'disable_serotype': True}.items()))
    else:
        # run the much faster vf and serotyping separately of amr
        j1 = high.enqueue(savvy, dict(args_dict.items() +
                                 {'disable_amr': True}.items()))
        j2 = low.enqueue(savvy, dict(args_dict.items() +
                                {'disable_vf': True, 'disable_serotype': True}.items()))
        time.sleep(60)
        insert(j1.result)
        insert(j2.result)



def monitor():
    '''
    Meant to run until all jobs are finished. Monitors queues and adds completed graphs to Blazegraph.
    '''
    sregistry = StartedJobRegistry(connection=redis_conn)
    fregistry = FinishedJobRegistry(connection=redis_conn)
    print high.get_job_ids()
    print sregistry.get_job_ids()
    while sregistry.get_job_ids():
        print 'in sregistry...'
        print fregistry.get_job_ids()
        for job_id in fregistry.get_job_ids():
            job=Job.fetch(job_id, connection=redis_conn)
            # sanity check
            if type(job.result) is Graph:
                print ('inserting', job_id, job)
                logging.info('inserting', job_id, job)
                insert(job.result)
        print 'sleeping 5'
        time.sleep(5)

    print 'all jobs complete'
    logging.info('monitor() exiting...all jobs complete')


def spfyids_single(args_dict):
    from settings import database

    # this is temporary, TODO: include a spqarql query to the db
    uriIsolate = gu(':spfy' + str(database['count']))

    uriGenome = gu(':' + generate_hash(args_dict['i']))

    args_dict['uriIsolate'] = uriIsolate
    args_dict['uriGenome'] = uriGenome

    return args_dict


def spfyids_directory(args_dict):
    '''
    TODO: make the database count actually work
    This is meant to preallocate spfyIDs
    -note may have problems with files that fail (gaps in id range)
    TODO: fix that^
    '''
    from settings import database
    files = os.listdir(args_dict['i'])
    count = database['count']
    uris = {}
    for f in files:
        uris[f] = {}
        uris[f]['uriIsolate'] = gu(':spfy' + str(count))
        uris[f]['uriGenome'] = gu(
            ':' + generate_hash(args_dict['i'] + '/' + f))
        count = count + 1

    args_dict['uris'] = uris

    # TODO: write-out count

    return args_dict


def spfy(args_dict):
    '''
    '''
    # check if a directory was passed or a just a single file
    # updates args_dict with appropriate rdflib.URIRef's
    if os.path.isdir(args_dict['i']):
        args_dict = spfyids_directory(args_dict)
    else:
        args_dict = spfyids_single(args_dict)

    print 'Starting blob_savvy call'
    logging.info('Starting blob_savvy call...')
    blob_savvy(args_dict)
    logging.info('blob_savvy enqueues finished')

    '''
    logging.info('starting monitor()...')
    monitor()
    print 'monitor exited...in spfy()'
    logging.info('monitor exited...in spfy()')
    '''

if __name__ == "__main__":
    import argparse

    from ConfigParser import SafeConfigParser

    # parsing cli-input
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="FASTA file or directory",
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

    args = parser.parse_args()
    # we make a dictionary from the cli-inputs and add are uris to it
    # mainly used for when a func needs a lot of the args
    args_dict = vars(args)

    # starting logging
    # TODO: move this to global and see it if breaks
    logging.basicConfig(
        filename='outputs/spfy' + __name__ + '.log',
        level=logging.INFO
    )

    spfy(args_dict)

    print('ALL COMPLETE')
    logging.info('ALL COMPLETE')
