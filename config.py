import pathlib

class Config:
    DATA_DIR = pathlib.Path("data")
    RESULTS_DIR = pathlib.Path("results")
    REFERENCE_DIR = DATA_DIR / "references"
    
    # Arquivos de entrada
    CRAM = DATA_DIR / "NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram"
    BED = DATA_DIR / "hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed"
    
    # Referência
    FASTA = REFERENCE_DIR / "Homo_sapiens_assembly38.fasta"
    
    # Opções para arquivos .dat (GRCh38)
    VERIFYBAMID_DAT_OPTIONS = {
        '100k': {
            'base_url': 'https://github.com/Griffan/VerifyBamID/raw/master/resource/',
            'files': {
                'UD': '1000g.phase3.100k.b38.vcf.gz.dat.UD',
                'V': '1000g.phase3.100k.b38.vcf.gz.dat.V',
                'bed': '1000g.phase3.100k.b38.vcf.gz.dat.bed',
                'mu': '1000g.phase3.100k.b38.vcf.gz.dat.mu'
            }
        },
        '10k': {
            'base_url': 'https://github.com/Griffan/VerifyBamID/raw/master/resource/',
            'files': {
                'UD': '1000g.phase3.10k.b38.vcf.gz.dat.UD',
                'V': '1000g.phase3.10k.b38.vcf.gz.dat.V',
                'bed': '1000g.phase3.10k.b38.vcf.gz.dat.bed',
                'mu': '1000g.phase3.10k.b38.vcf.gz.dat.mu'
            }
        }
    }
    
    # Escolha padrão (pode ser modificada via linha de comando)
    SELECTED_DAT_VERSION = '100k'  # ou '10k'