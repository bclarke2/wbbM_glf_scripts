"""
This script reads a Blast .xml file and generates a file with the genome accession number
and hsp start position of the alignment, comma-delineated on separate lines.

You must have Biopython installed.
The attributes holding the specific information from the xml file are described in
the Biopython Tutorial web page.
e.g., <Hit_id> in the xml file is stored in the .title attribute in the
object created by NCBIXML.read()
Change the file name variables as you need.
"""
from Bio.Blast import NCBIXML

infilename = '<yourinputfile.xml>'
outfilename = '<youroutputfile.txt>'

result_handle = open(infilename)
blast_result = NCBIXML.read(result_handle)
# list that will hold tuples containing (accession, hspstart)
name_start = []
# alignment may have >1 hsp, so loop through all of these,
# extract the 4th item from the pipe-delineated title,
# (this will be the accession number)
# append a tuple with the acc/startsite pairs in the list.
for alignment in blast_result.alignments:
    for hsp in alignment.hsps:
        accession = alignment.title.split('|')[3]
        hsp_start = hsp.sbjct_start
        name_start.append((accession, hsp_start))

result_handle.close()
out_handle = open(outfilename, 'w')
# iterate through the list and print out the tuple values
# into the file.
for item in name_start:
    acc, strt = item
    out_handle.write(acc + ',' + str(strt) + '\n')
out_handle.close()
# print(name_start)
