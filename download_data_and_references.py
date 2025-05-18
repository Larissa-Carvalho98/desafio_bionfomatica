import argparse
from config import Config
import logging
from pathlib import Path
import requests

Path("results").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
Path("data/references").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("results") / "download_references.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def download_file(url: str, output_path: Path) -> None:
    """Baixa arquivo com tratamento de erro"""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"Arquivo baixado: {output_path}")
    except Exception as e:
        logger.error(f"Erro ao baixar {url}: {str(e)}")
        raise

def download_main_data_files():
    """Baixa arquivos principais de dados (.cram, .crai, .bed)"""
    files = [
        (
            "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/data/CEU/NA06994/exome_alignment/NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram",
            Config.CRAM
        ),
        (
            "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/data/CEU/NA06994/exome_alignment/NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram.crai",
            Config.DATA_DIR / "NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram.crai"
        ),
        (
            "https://www.twistbioscience.com/sites/default/files/resources/2022-12/hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed",
            Config.BED
        ),
    ]
    for url, dest in files:
        if not dest.exists():
            logger.info(f"Baixando {dest.name}...")
            download_file(url, dest)
        else:
            logger.info(f"{dest.name} já existe, pulando download.")

def download_reference_fasta():
    """Baixa o arquivo de referência .fasta"""
    fasta_url = "https://storage.googleapis.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta"
    if not Config.FASTA.exists():
        logger.info(f"Baixando {Config.FASTA.name}...")
        download_file(fasta_url, Config.FASTA)
    else:
        logger.info(f"{Config.FASTA.name} já existe, pulando download.")

def download_verifybamid_resources(dat_version: str = '100k') -> bool:
    """Baixa todos os arquivos necessários para uma versão específica"""
    if dat_version not in Config.VERIFYBAMID_DAT_OPTIONS:
        logger.error(f"Versão {dat_version} não disponível. Opções: {list(Config.VERIFYBAMID_DAT_OPTIONS.keys())}")
        return False
    
    resource_dir = Config.REFERENCE_DIR / "verifybamid2"
    resource_dir.mkdir(exist_ok=True)
    
    files = Config.VERIFYBAMID_DAT_OPTIONS[dat_version]['files']
    base_url = Config.VERIFYBAMID_DAT_OPTIONS[dat_version]['base_url']
    
    all_success = True
    for file_type, filename in files.items():
        dest_path = resource_dir / filename
        if not dest_path.exists():
            try:
                url = base_url + filename
                logger.info(f"Baixando {filename}...")
                download_file(url, dest_path)
            except Exception as e:
                logger.error(f"Falha ao baixar {filename}: {str(e)}")
                all_success = False
        else:
            logger.info(f"{filename} já existe, pulando download.")
    return all_success

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verifybamid', choices=['100k', '10k'], default='100k',
                       help='Versão dos arquivos do VerifyBamID2 a baixar')
    args = parser.parse_args()
    
    logger.info("Baixando arquivos principais de dados (.cram, .crai, .bed)...")
    download_main_data_files()
    logger.info("Baixando arquivo de referência .fasta...")
    download_reference_fasta()
    logger.info(f"Baixando arquivos do VerifyBamID2 ({args.verifybamid})...")
    success = download_verifybamid_resources(args.verifybamid)
    
    if success:
        print("Todos os arquivos foram baixados com sucesso!")
    else:
        print("Alguns arquivos não puderam ser baixados. Verifique os erros acima.")

if __name__ == "__main__":
    main()