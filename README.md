## ATG_fastq_merger

This script uses FLASH with default parameters to merge paired-end illumina reads.


## Requirements
* `flash` package: can be installed via [conda](https://anaconda.org/bioconda/flash).
* `python3`
* Tested on a linux machine, no reason to not to work on Mac and Windows.

## Usage 

### Single sample
`python merger.py [--sample-name SAMPLE_NAME] [--read1 READ1] [--read2 READ2] [--out-dir PATH_TO_OUTPUT_DIR]`

or

`python merger.py [-n SAMPLE_NAME] [-r1 READ1] [-r2 READ2] [-o PATH_TO_OUTPUT_DIR]`
    
### A list of samples:

Prepare a tab delimited `SAMPLES_TSV` file with the following headers `sample_name`,`read1`,`read2`. For example:

| sample_name  | read1                   | read2                 |
| ------------ | ----------------------- | --------------------- |
| mysample_1   | whatever1.R1.fastq.gz   | whatever1.R2.fastq.gz |
| mysample_2   | whatever2.R1.fastq.gz   | whatever2.R2.fastq.gz |


`python merger.py [--samples-file PATH_TO_SAMPLES_TSV] [--out-dir PATH_TO_OUTPUT_DIR]`

or

`python merger.py [-f PATH_TO_SAMPLES_TSV] [-o PATH_TO_OUTPUT_DIR]`

    
**Important Note**: `sample_name` must be alphanumeric (*i.e.*, avoid &, $, @, -, %, * and empty space in the file names).

## Outputs
* `out_dir/sample_name.fastq` contains the fastq file(s).
* `out_dir/merger_stats.tsv` contains the FLASH statistics (TotalPairs, CombinedPairs, UncombinedPairs, PercentCombined) per sample. 

### References
* **FLASH** : Magoč T, Salzberg SL. FLASH: fast length adjustment of short reads to improve genome assemblies. Bioinformatics. 2011 Nov 1;27(21):2957-63. doi: 10.1093/bioinformatics/btr507. Epub 2011 Sep 7. PMID: 21903629; PMCID: PMC3198573.
    
### Bugs
Please report errors/bugs to: Amir.Taheri.Ghahfarokhi@gmail.com
