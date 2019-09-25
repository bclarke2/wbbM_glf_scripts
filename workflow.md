## Workflow to identify bacterial strains with *wbbM* and *glf* at the same locus

1) Prepare a fasta file of the sequence you wish to perform a blast query with.
2) Use `queryBLAST.py` to perform a blast search and store the results in a .xml file.
3) Use `get_accession_hspstart.py` to parse the xml file and produce a comma-separated
    listing of nucleotide accession numbers and hsp start positions.
4) Use `genome_scan.py` to download each genbank record referenced by the accessions
    and identify the *wbbM* ORF and look for *glf* within 7,000 nt. This produces a
    file with the translation and other relevant information.
