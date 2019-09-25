# This script performs a blast query from a sequence in the file referenced in the variable
# inputFile. tnlastn looks in the translated nucleotide database.
# The output (outputFile) is an xml file of the results of the blast search.
# See the source code for the Biopython Bio.Blast module for the parameters that can be used
# This script was written to be  specific to my needs at the time but theparameters can be changed
# by initializing the variables differently.

from Bio.Blast import NCBIWWW

inputFile = '<yourinputfile.fasta>'
# the type of blast search
prog = 'tblastn'
# the database to be queried
databs = 'nr'
evalue = 10e-15
# maximum number of hits returned
resSize = 10000
outputFile = '<youroutputfile.xml>'

query_sequence = open(inputFile).read()
result_handle = NCBIWWW.qblast(prog, databs, query_sequence, expect=evalue, hitlist_size=resSize)
with open(outputFile, "w") as out_handle:
    out_handle.write(result_handle.read())
result_handle.close()


