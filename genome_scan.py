"""
This script requires that Biopython is installed on your system.
This script was used to identify the DUF4422 ORF(s) on nucleotide sequences
retrieved from the NCBI Entrez database and search for the glf gene
within 7000 nt of that ORF. It takes as input, a file of nt accession
identifiers and the start position of HSPs derived from a blast search
result. ie., accession, hsp_start_position are comma separated with
one set of values per line. This file can be generated by parsing
a BLAST xml file with the script, get_accession_hspstart.py

genome_scan.py uses epost to post the accessions to Entrez and the
history feature of Entrez is used to fetch the genbank sequences,
one at a time, parse them to find the ORF with DUF4422 and search
for the annotation(s) referenced in SEARCHWORDS.

Note that the postuuid() funcion requires a list of accessions
for input and this must be derived from your file yourself
if you are imoprting this as a module.
The output file is written to in the fetchfasta_entrez_parse()
function and the filename (as with all constants) can be
overwritten in the importing script. I would like to refactor
this in the future to hav the function return a variable to
be written to a file external to the function.

The general idea for this script was given to me by a script
from Evan Mann formerly of the Dept of Mol and Cell
Biology, University of Guelph. I have rewritten his to accomodate
my specific application. I also used someones script as a skeleton
for the post and fetch but I cannot remember where 
I saw it after a number of years.
"""

import sys, time
from Bio import Entrez
from Bio import SeqIO


Entrez.email = 'bclarke@uoguelph.ca'
Entrez.api_key = '09ea25f030032e76969cb1267ff153964708'

DATABASE = 'nucleotide'
BATCHSIZE = 1
OUTPUTFILENAME = 'wbbM_plus_glf.txt'
RETTYPE = 'gb'
SEARCHWORDS = ['udp-galactopyranose mutase', 'glf']

def postuuids(idlist, database):

    # This function posts the uuids to Entrez to be used with their history feature
    # The uuids (accessions) must be supplied as a list of strings.
    # See the Biopython source code for the available databases.
    request = Entrez.epost(db=database, id=','.join(idlist))
    print('\nThe epost request was successful.')
    try:
        result = Entrez.read(request)
    except RuntimeError as e:
        print('\nAn error occured while parsing the request')
        print('Error: {}'.format(e))
        sys.exit(-1)
    
    # Entrez.epost returns a queryKey and webEnv variable to be used
    # in the history feature to fetch the data.
    queryKey = result['QueryKey']
    webEnv = result['WebEnv']
    print('\nQueryKey = {0}\nWebEnv = {1}'.format(queryKey, webEnv))
    return queryKey, webEnv

def fetchfasta_entrez_parse(queryKey, webEnv, count, wbbMHspList):
    
    # This function fetches the data and writes to a file
    # queryKey and webEnv are returned by the postuuids method.
    # wbbMHspList is a list of the start sites for the HSPs (blast high scoring pairs).
    # count is the number of uuids and will be used to keep track of
    # the records being fetched below.
    from urllib.error import HTTPError
    # start glfPresent as false initially
    glfPresent = False
    glfCounter = 0
    keywords = SEARCHWORDS
    hspIndex = 0
    # Recommended to run fetches in small batches for large sequences
    # Here, I want to download only one at a time, process it and then repreat.
    # Thus, batch size will be 1. 
    batchSize = BATCHSIZE
    results_file = open(OUTPUTFILENAME, 'w')
    # format a header and write as the 1st line of the file.
    header = '{0}\t{5}\t{6}\t{1}\t{2}\t{3}\t{4}\n'.format('organism', 'protein_id', 'nucl_accession', 'prot_length', 'translation', 'strain', 'serotype')
    results_file.write(header)
    for start in range(0, count, batchSize):
        end = min(count, start + batchSize)
        print('Downloading record(s) {0} to {1}\n'.format(start + 1, end))
        # In case of network error, attempt 3 times with a pause between each attempt.
        attempt = 0
        while attempt < 3:
            attempt += 1
            try:
                # This handle holds the data.
                fetchHandle = Entrez.efetch(
                        db=DATABASE,
                        rettype=RETTYPE,
                        retmode='text',
                        retstart=start,
                        retmax=batchSize,
                        webenv=webEnv,
                        query_key=queryKey,
                        idtype='acc'
                        )
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print('Received an error from the server: {}'.format(err))
                    print('Attempt {} of 3.'.format(attempt))
                    print("pausing...")
                    time.sleep(2)
                else:
                    raise
        # Store the data as a SeqIO object in memory.
        record  = SeqIO.read(fetchHandle, 'gb')
        fetchHandle.close()
        print('Data read.\n')
        print('Parsing sequence data.\n')
        # accession is the .id attribute
        genBankacc = record.id
        # initialize the following variables in the top level
        # scope of the function so they can be used outside of
        # loops below.
        proteinID = ''
        organism = ''
        strain = ''
        serotype = ''
        translation = ''
        wbbMLength = 0
        wbbMStartPosition = 0
        wbbMEndPosition = 0
        # cycle through all the features in the record
        # pull out organism info from the "source" feature.
        for feature in record.features:
            # find the "source" and pull out organism name.
            if feature.type == 'source':
                organism = feature.qualifiers['organism'][0]
                # these may not exist so wrap them in try statements
                try:
                    strain = feature.qualifiers['strain'][0]
                except:
                    strain = ''
                try:
                    serotype = feature.qualifiers['serotype'][0]
                except:
                    serotype = ''
        for feature in record.features:
            # avoid joins.
            # also, some hsp starts were less than the actual ORF start due
            # to errors so I tacked on 15 as an arbitrary hsp start number to find the ORF
            # encompassing the hsp.
            if feature.type == 'CDS' and \
                    feature.location_operator != 'join' and \
                    feature.location.start.position <= (wbbMHspList[hspIndex] + 15) and \
                    feature.location.end.position >= (wbbMHspList[hspIndex] + 15):
                wbbMStartPosition = feature.location.start.position
                wbbMEndPosition = feature.location.end.position
                # amino acid length from the ORF
                wbbMLength = (abs(feature.location.end.position - feature.location.start.position)) / 3
                print(feature.type, feature.location.start.position, wbbMHspList[hspIndex])
                print(wbbMStartPosition, wbbMEndPosition)
                # qualifiers is a dictionary of lists
                try:
                    translation = feature.qualifiers['translation'][0]
                except:
                    translation = ''
                try:
                    proteinID = feature.qualifiers['protein_id'][0]
                except:
                    proteinID = ''
        for feature in record.features:
            # find CDS within 7000 nt up or down from the wbbM ORF
            if feature.type == 'CDS':
                if feature.location.start.position <  (wbbMStartPosition + 7000) and feature.location.start.position >  (wbbMStartPosition - 7000):
                    # create a set and add gene names of products to the set from the +/- 7000 nt range
                    # the set is newly created for each "positive" CDS feature
                    # used the .get() method in case the dict key does not exist to prevent key errors
                    neighbours = set()
                    if feature.qualifiers.get('gene'):
                        neighbours.add(feature.qualifiers.get('gene')[0])   
                    if feature.qualifiers.get('product'):
                        geneProduct = feature.qualifiers['product'][0]
                        neighbours.add(geneProduct.lower())
                    #print()
                    #print(geneProduct)
                    #print(neighbours)
                    #print(keywords)
                    # if neighbours set and keywords set intersect, then glf is present.
                    if any(i in neighbours for i in keywords):
                        glfPresent = True
                        glfCounter += 1
                        break

        print('\nGlf present: {}\n'.format(glfPresent))
        print('Nucl. Accession: ' + genBankacc + '\n')
        # if glf is present, format the data and write to a line in the output file.
        if glfPresent:
            dataLine = '{0}\t{5}\t{6}\t{1}\t{2}\t{3}\t{4}\n'.format(organism, proteinID, genBankacc, wbbMLength, translation, strain, serotype)
            results_file.write(dataLine)
            print(proteinID)
            print(organism)
            print(translation)

        # set glfPresent back to false after writing a line.
        glfPresent = False
        hspIndex += 1
        print('\nFiles processed: {0} of {1}'.format(hspIndex, count))
        print('{0} instances of UDP-galactopyranose mutase (Glf) found.'.format(glfCounter))
    
    results_file.close()

if __name__ == '__main__':
    
    import sys
    from Bio import Entrez
    from Bio import SeqIO

    Entrez.email = 'bclarke@uoguelph.ca'
    Entrez.api_key = '09ea25f030032e76969cb1267ff153964708'
    DATABASE = 'nucleotide'
    BATCHSIZE = 1
    OUTPUTFILENAME = 'wbbM_plus_glf.txt'
    RETTYPE = 'gb'
    SEARCHWORDS = {'udp-galactopyranose mutase', 'glf'}
    
    # This file must be comma-separated accessions and hsp start nos
    # -one set of them per line.
    hitsFile = input('Enter the input file: ')
    fileHandle = open(hitsFile)
    accessionList = []
    hspListTmp = []
    for line in fileHandle:
        accessionList.append(line.split(',')[0])
        hspListTmp.append(line.split(',')[1].rstrip('\n'))
    fileHandle.close()
    # convert the hsp nos from strings to integers.
    hspList = list(map(int, hspListTmp))
    count = len(accessionList)
    queryKey, webEnv = postuuids(accessionList, DATABASE)
    fetchfasta_entrez_parse(queryKey, webEnv, count, hspList)



