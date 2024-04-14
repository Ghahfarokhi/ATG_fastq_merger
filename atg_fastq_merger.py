# ATG_fastq_merger.py 
# Version: 20240413
# Author: Amir Taheri-Ghahfarokhi
# Contact: 
#        Email: Amir.Taheri.Ghahfarokhi@Gmail.com
#        Linkedin: https://www.linkedin.com/in/ghahfarokhi/


import argparse
import pandas as pd
import subprocess
import os
import re
import sys

def check_samples_file(samples_file):
    """Check if the input file contains the required columns."""
    if not os.path.exists(samples_file):
        sys.exit("Error: The provided samples file does not exist.")

    df = pd.read_csv(samples_file, sep="\t")
    
    required_columns = ["sample_name", "read1", "read2"]
    input_columns = df.columns.tolist()
    missing_columns = [col for col in required_columns if col not in input_columns]

    if missing_columns:
        sys.exit(f"ERROR: Input file is missing the following required columns: {', '.join(missing_columns)}")
    else:
        return df


def run_flash(sample_name, read1, read2, out_dir):
    log_file = os.path.join(out_dir, sample_name + ".flash.log")
    command = ["flash", read1, read2, "-o", os.path.join(out_dir, sample_name)]
    with open(log_file, 'w') as f:
        result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE)
        if result.returncode != 0:
            error_message = f"Error running flash for sample {sample_name}: {result.stderr.decode()}"
            print(error_message)
            return None
    return log_file

def parse_flash_log_file(log_file):
    total_pairs = None
    combined_pairs = None
    uncombined_pairs = None
    percent_combined = None

    with open(log_file, "r") as log:
        lines = log.readlines()
        for line in lines:
            total_pairs_match = re.search(r"Total pairs:\s+(\d+)", line)
            combined_pairs_match = re.search(r"Combined pairs:\s+(\d+)", line)
            uncombined_pairs_match = re.search(r"Uncombined pairs:\s+(\d+)", line)
            percent_combined_match = re.search(r"Percent combined:\s+([\d.]+)%", line)

            if total_pairs_match:
                total_pairs = int(total_pairs_match.group(1))
            elif combined_pairs_match:
                combined_pairs = int(combined_pairs_match.group(1))
            elif uncombined_pairs_match:
                uncombined_pairs = int(uncombined_pairs_match.group(1))
            elif percent_combined_match:
                percent_combined = float(percent_combined_match.group(1))

    return total_pairs, combined_pairs, uncombined_pairs, percent_combined

def clean_unwanted_flash_files(sample_name, out_dir):
    os.rename(os.path.join(out_dir, sample_name + ".extendedFrags.fastq"), os.path.join(out_dir, sample_name + ".fastq"))
    os.remove(os.path.join(out_dir, sample_name + ".flash.log"))
    os.remove(os.path.join(out_dir, sample_name + ".hist"))
    os.remove(os.path.join(out_dir, sample_name + ".histogram"))
    os.remove(os.path.join(out_dir, sample_name + ".notCombined_1.fastq"))
    os.remove(os.path.join(out_dir, sample_name + ".notCombined_2.fastq"))



def print_help():
    help = """
    This script uses FLASH with default parameters to merge paired-end illumina reads.
    Author: Amir.Taheri.Ghahfarokhi@Gmail.com
    Version: 20240413
    
    usage:
    For merging R1 and R2 for a single sample:

        python merger.py [--sample-name SAMPLE_NAME] [--read1 READ1] [--read2 READ2] [--out-dir PATH_TO_OUTPUT_DIR]
        or
        python merger.py [-n SAMPLE_NAME] [-r1 READ1] [-r2 READ2] [-o PATH_TO_OUTPUT_DIR]
    
    For merging R1 and R2 for a list of samples listed in a samples-file:

        python merger.py [--samples-file PATH_TO_SAMPLES_TSV] [--out-dir PATH_TO_OUTPUT_DIR]
        or
        python merger.py [-f PATH_TO_SAMPLES_TSV] [-o PATH_TO_OUTPUT_DIR]

    Important Note 1: 
    SAMPLES_TSV file is expected to be tab-delimited file with the following header:
    sample_name	read1	read2
    
    Important Note 2: 
    sample_name must be alphanumeric (i.e., avoid &, $, @, -, %, * and empty space in the file names)

    References
    FLASH : Magoč T, Salzberg SL. FLASH: fast length adjustment of short reads to improve genome assemblies. Bioinformatics. 2011 Nov 1;27(21):2957-63. doi: 10.1093/bioinformatics/btr507. Epub 2011 Sep 7. PMID: 21903629; PMCID: PMC3198573.
    
    """

    print(help)

def parse_arguments():
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(1)
        
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-n', "--sample-name")
    parser.add_argument('-r2', "--read1")
    parser.add_argument('-r1', "--read2")
    parser.add_argument('-f', "--samples-file")
    parser.add_argument('-o', "--out-dir")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS)
    return parser.parse_args()

def main():

    args = parse_arguments()

    if args.out_dir:
        # Check if the output directory exists, if not, create it
        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)
    else:
        print_help()
        sys.exit("ERROR: argument --out-dir is not provided!")

    out_dir = args.out_dir

    if args.sample_name and args.read1 and args.read2:
        sample_name = args.sample_name
        read1 = args.read1
        read2 = args.read2
        print(f"Running FLASH for sample {sample_name}")
        log_file = run_flash(sample_name, read1, read2, out_dir)
        if log_file:
            total_pairs, combined_pairs, uncombined_pairs, percent_combined = parse_flash_log_file(log_file)
            if None in (total_pairs, combined_pairs, uncombined_pairs, percent_combined):
                print(f"Error: Required information not found in flash log file for sample {sample_name}")
                return
            else:
                print(f"sample_name: {sample_name}, TotalPairs: {total_pairs}, PercentCombined: {percent_combined}")
        
        clean_unwanted_flash_files(sample_name, out_dir)

    elif args.samples_file:
        samples_file = args.samples_file
        
        df = check_samples_file(samples_file)

        # Making column names lower case 
        df.columns = map(str.lower, df.columns)

        for index, row in df.iterrows():
            sample_name = row["sample_name"]
            read1 = row["read1"]
            read2 = row["read2"]

            print(f"Running FLASH for sample {sample_name}")
            log_file = run_flash(sample_name, read1, read2, out_dir)
            if log_file:
                total_pairs, combined_pairs, uncombined_pairs, percent_combined = parse_flash_log_file(log_file)
                if None in (total_pairs, combined_pairs, uncombined_pairs, percent_combined):
                    print(f"Error: Required information not found in flash log file for sample {sample_name}")
                    continue
                else:
                    print(f"sample_name: {sample_name}, TotalPairs: {total_pairs}, PercentCombined: {percent_combined}")
                    # Add statistics as new columns to the DataFrame
                    df.loc[index, "TotalPairs"] = total_pairs
                    df.loc[index, "CombinedPairs"] = combined_pairs
                    df.loc[index, "UncombinedPairs"] = uncombined_pairs
                    df.loc[index, "PercentCombined"] = percent_combined

            clean_unwanted_flash_files(sample_name, out_dir)
        
        # Save the updated DataFrame back to the TSV file
        stat_file = os.path.join(out_dir, "merger_stats.tsv")
        df.to_csv(stat_file, sep="\t", index=False)

        print(f"Merger is done! flash statistics are saved here: {stat_file}\n")

    else:
        print_help()

if __name__ == "__main__":
    main()
