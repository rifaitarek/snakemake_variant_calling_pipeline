genome_db = "/chr9.fa"
snpeff_jar = "/snpEff.jar"
snpeff_genome = 'hg38'
snpeff_db_folder = '/snpeff_db'


# list of sample names to process.
sample_names, = glob_wildcards("000.fastq/{sample}.fastq")


#All the expected outputs
rule all:
    input:
        fastqc_zip=expand("010.fastqc/{sample}_fastqc.zip", sample=sample_names),
        summary_png=expand("010.fastqc/{sample}_fastqc/summary.png", sample=sample_names),
        rep1=expand("010.fastqc/{sample}_fastqc/Images/per_base_quality.png", sample=sample_names),
        vcf="030.samtools/snps.vcf",
        cleaned_vcf="040.cleaned/snps.cleaned.vcf",
        snpeff = "050.snpeff/snps.annotated.vcf",




rule fastqc:
    input:
        fq="000.fastq/{file}.fastq",
    output:
        fastqc_zip="010.fastqc/{file}_fastqc.zip",
        html="010.fastqc/{file}_fastqc.html",
        summarydata="010.fastqc/{file}_fastqc/fastqc_data.txt",
        rep1=report("010.fastqc/{file}_fastqc/Images/per_base_quality.png", category="Fastqc",
                    subcategory="Per base quality", labels={"sample": "{file}"}),
        rep2=report("010.fastqc/{file}_fastqc/Images/per_base_sequence_content.png", category="Fastqc",
                     subcategory="Per base sequence content", labels={"sample": "{file}"}),
        rep3=report("010.fastqc/{file}_fastqc/summary.txt", category="Fastqc",
                    subcategory="Summary text", labels={"sample": "{file}"}),
    shell:
        """
        echo "Input Fastq: {input.fq} "
        fastqc -o 010.fastqc {input.fq} --extract

        if grep FAIL {output.rep3}; then
            # Found a fail! -
            echo "FAILED!"
            # false yields a non-zero return code - which is an error
            false
        fi

        """


rule bwa:
    input:
        fq="000.fastq/{sample}.fastq",
    output:
        bam = "020.bwa/{sample}.bam",
        bai = "020.bwa/{sample}.bam.bai",
    params:
        db = genome_db,
    shell:
        """
        bwa mem {genome_db} {input.fq} \
            | samtools sort - \
            > {output.bam}
        samtools index {output.bam}
        """


rule variant_calling:
    input:
        db=genome_db,
        bams=expand("020.bwa/{sample}.bam", sample=sample_names),
    output:
        vcf="030.samtools/snps.vcf",
    shell:
        """
        echo '+-------------------------'
        echo '| processing {input.bams}'
        echo '+-------------------------'

        bcftools mpileup -Ou -f {input.db} {input.bams} \
             | bcftools call -mv -Ov -o {output.vcf}

        """


rule variant_cleanup:
    input:
        db=genome_db,
        vcf="030.samtools/snps.vcf"
    output:
        vcf="040.cleaned/snps.cleaned.vcf"
    shell:
        """
        ( cat {input.vcf} \
           | vt decompose - \
           | vt normalize -n -r {input.db} - \
           | vt uniq - \
           | vt view -f "QUAL>20" -h - \
           > {output.vcf} )


        """


rule snpeff:
    input:
        vcf = "040.cleaned/snps.cleaned.vcf",
    params:
        snpeff_db_folder = snpeff_db_folder,
        snpeff_jar = snpeff_jar,
        snpeff_genome = snpeff_genome,
    log:
        err="050.snpeff/snakemake.err",
    output:
        vcf = "050.snpeff/snps.annotated.vcf",
        html = "050.snpeff/snpEff_summary.html",
        genetxt = "050.snpeff/snpEff_genes.txt",
    shell:
        """

        mkdir -p 050.snpeff

        java -Xmx4096m -jar \
            {params.snpeff_jar} eff {params.snpeff_genome} \
            -dataDir {params.snpeff_db_folder} \
            {input.vcf} > {output.vcf}

        # move output files to the snpeff output folder
        mv snpEff_genes.txt snpEff_summary.html 050.snpeff

        """



rule fastqc_report_image:
    input:
        summarytxt = "010.fastqc/{file}_fastqc/summary.txt"
    output:
        statuspng = report("010.fastqc/{file}_fastqc/summary.png",
                         category='Fastqc',
                         subcategory='Status',
                         labels={"sample": "{file}"})

    run:
        import pandas as pd
        import seaborn as sns
        import matplotlib.pyplot as plt

        #load data
        data = pd.read_csv(input.summarytxt, sep="\t", header=None)
        data.columns = ['status', 'test', 'sample']

        #assign dummy x value for scatterplot
        data['x'] = 1

        #create image
        fig = plt.figure(figsize=(4,5))
        ax = plt.gca()
        sns.scatterplot(data, x='x', y='test', hue='status', s=200, ax=ax)
        ax.get_xaxis().set_visible(False)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.title(wildcards.file)
        plt.savefig(output.statuspng)
