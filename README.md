## wbbM_glf_scripts

- `queryBLAST.py`
   Used to obtain an xml file of blast results by querying the NCBI databases

- `get_accession_hspstart.py
   Used to generate a file of accession, hsp_start pairs from the blast result.

- `genome_scan.py`  
   Downloads and scans the nucleotide sequences from the accession, hsp_start
   file and identifies the *glf* ORF within 7000 nt of the proteins identified
   from the blast query.
