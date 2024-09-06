# Snakemake Variant Calling Pipeline

## Table of Contents
- [Purpose](#Purpose)
- [Data](#Data)
- [Configure the pipeline](#Configurethepipeline)
- [Run the pipeline](#Runthepipeline)
- [Output](#Output)
- [Dependencies](#Dependencies)
- [Additional Notes](#AdditionalNotes)
- [Clone the repository](#Clonetherepository)


## Purpose

This Snakemake pipeline automates the process of variant calling from FASTQ files, using tools like BWA, Samtools, and SnpEff. It incorporates quality control steps using FastQC and variant filtering and annotation.


## Data

Ensure your FASTQ files are organized in a directory named 000.fastq.
Create necessary directories: 010.fastqc, 020.bwa, 030.samtools, 040.cleaned, and 050.snpeff.


## Configure the pipeline

**genome_db**: Replace with the path to your reference genome.
**snpeff_jar**: Replace with the path to the SnpEff JAR file.
**snpeff_genome**: Set the appropriate SnpEff genome version.
**snpeff_db_folder**: Replace with the path to the SnpEff database folder.


## Run the pipeline
bashCopysnakemake


## Output
The pipeline will generate the following output files in the specified directories:

**FASTQC**: Summary reports and quality control plots for each FASTQ file.
**BWA**: Aligned BAM files and their indices.
**Samtools**: Variant call VCF files.
**Cleaned**: Filtered and normalized VCF files.
**SnpEff**: Annotated VCF files, along with summary and gene annotation reports.


## Dependencies

- Snakemake
- BWA
- Samtools
- SnpEff
- FastQC
- Python libraries (Pandas, Seaborn, Matplotlib)


## Additional Notes

The pipeline is highly customizable. You can modify parameters, add or remove steps, and incorporate additional tools as needed.
For more information on Snakemake and its features, refer to the official documentation.

## Clone the repository

```bash
bashCopygit clone https://github.com/your_username/snakemake_variant_calling_pipeline
