#views.py
"""
views.py
provides the endpoints for this particular blueprint. Each endpoint is
responsible for putting the data into an appropraite format.
"""
import os
from flask import jsonify, request
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

from werkzeug import secure_filename

from superphy.shared import sparql
from . import data
from ..models import Response

@data.after_request
def add_header(response):
    """
    Append after request the nessesary headers.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = "accept, content-type"
    return response

"""
@data.route('/meta', methods=['GET', 'POST'])
def meta():
    #General query that returns all genomes and their metadata.

    results = (sparql.get_all_genome_metadata())
    results['date'] = (datetime.datetime.now() + datetime.timedelta(minutes=30)).isoformat()
    return jsonify(results)
"""
@data.route('/meta', methods=['GET'])
def meta2():
    """
    General query that returns all genomes and metadata.
    """
    return Response.default(sparql.get_all_genome_metadata())

@data.route('/genomes', methods=['GET', 'POST'])
def genomes():
    """
    General query that returns all genomes and their metadata.
    """
    return Response.default(sparql.get_all_genome_metadata())

@data.route('/genome/<genomeid>', methods=['GET', 'POST'])
def genome(genomeid):
    """
    Returns the metadata of a particular genome in json format.
    """
    return Response.default(sparql.get_genome_metadata(genomeid))

@data.route('/genes', methods=['GET', 'POST'])
def genes():
    """
    General query that returns all genes and their metadata.
    """
    return Response.default(sparql.get_all_genes())

@data.route('/vf', methods=['GET', 'POST'])
def vfs():
    """
    General query that returns all virulence factors.
    """
    return Response.default(sparql.get_all_genes('vf'))

@data.route('/amr', methods=['GET', 'POST'])
def amrs():
    """
    General query that returns all antimicrobial resistance genes.
    """
    return Response.default(sparql.get_all_genes('amr'))

@data.route('/gene/<geneid>', methods=['GET', 'POST'])
def gene(geneid):
    """
    Returns the metadata of a particular gene in json format.
    """
    return Response.default(sparql.get_gene(geneid))

@data.route('/regions/<genomeid>', methods=['GET', 'POST'])
def regions(genomeid):
    """
    Returns all the genes inside a particular genome
    """
    return Response.default(sparql.find_alleles(genomeid))

@data.route('/region/<geneid>/<genomeid>', methods=['GET', 'POST'])
def region(geneid, genomeid):
    """
    Queries for the instances of geneid in genomeid.
    """
    results = (sparql.find_regions(geneid, genomeid))
    return Response.default(results)

@data.route('/genesearchresults', methods=['POST'])
def genesearchresults():
    """
    Endpoint for returning gene search results
    """
    data_ = request.get_json()
    print "data", data_
    genomes_ = data_["genome"]
    genes_ = data_["genes"]

    ## Prepping dictionary to be returned
    genomeDict = {}
    for genome in genomes_:
        genomeDict[genome] = {}
        for gene in genes_:
            genomeDict[genome][gene] = 0
    
    results = sparql.get_regions(genomes_, genes_)
    bindings = results['results']['bindings']
    for binding in bindings:
        accession = binding['Genome']['value'].split("#")[1]
        gene_name = binding['Gene_Name']['value']
        try:
            genomeDict[accession][gene_name] += 1
        except KeyError:
            "Genome or gene doesn't exist in dictionary"

    return jsonify(genomeDict)


# results = (sparql.get_all_genome_metadata())
#     bindings = results['results']['bindings'][:5]
#     rows = []
#     for binding in bindings:
#         row = {}
#         for item in results['head']['vars']:
#             try:
#                 row[item] = binding[item]['value']
#             except KeyError:
#                 row[item] = ''
#         rows.append(row)
#     return jsonify({'data':rows})

# Uploading stuff (actually belongs in uploader)

class MyForm(Form):
    """
    This belongs in models. This is dummy  function.
    """
    name = StringField('name', validators=[DataRequired()])
#Change this later to only allow '.faldo'?
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@data.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    We also want to be changing the filename somehow, and keep track of who 
    is uploading what
    """
    if request.method == 'POST':
        file_ = request.files['file0']
        path = os.path.join(os.path.abspath(__file__)
            .split('superphy')[:2][:1].pop(), 'superphy/superphy/posted_files')
        print path
        if file and allowed_file(file_.filename):
            filename = secure_filename(file_.filename)
            file_.save(os.path.join(path, filename))
            return jsonify({})
    return jsonify({})
