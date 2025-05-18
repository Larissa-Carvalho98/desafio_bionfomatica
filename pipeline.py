import subprocess
from pathlib import Path
import os
import logging
import gzip
from typing import Tuple
from config import Config

# Garante que o diretório de resultados existe antes de configurar o logger
Path("results").mkdir(exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.RESULTS_DIR / "pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories() -> None:
    """Cria diretórios necessários se não existirem"""
    for directory in [Config.DATA_DIR, Config.RESULTS_DIR, Config.REFERENCE_DIR]:
        directory.mkdir(exist_ok=True, parents=True)
    logger.info("Diretórios configurados")

def check_file_exists(file_path: Path, description: str) -> None:
    """Verifica se arquivo existe e é acessível"""
    if not file_path.exists():
        logger.error(f"{description} não encontrado em: {file_path}")
        raise FileNotFoundError(f"{description} não encontrado")

def run_command(cmd: list, description: str) -> None:
    """Executa comando com tratamento de erros"""
    logger.info(f"Executando: {description}")
    logger.debug(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        logger.debug(f"Saída: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar {description}: {e.stderr}")
        raise

# Lê profundidade média de um arquivo summary.txt
def ler_profundidade_media(summary_file):
    with open(summary_file) as f:
        for line in f:
            if line.startswith("total_region"):
                cols = line.strip().split()
                return float(cols[3])  # profundidade média
    return 0.0

# Conta o número total de bases no BED
def calcular_bases_bed(bed_file):
    total = 0
    with open(bed_file) as f:
        for line in f:
            cols = line.strip().split()
            total += int(cols[2]) - int(cols[1])
    return total

# Calcula percentuais ≥10x e ≥30x
def calcular_percentuais(thresholds_file, bed_total_bases):
    cov10 = 0
    cov30 = 0
    with gzip.open(thresholds_file, "rt") as f:
        next(f)  # pula o cabeçalho
        for line in f:
            cols = line.strip().split()
            if len(cols) < 5:
                continue
            try:
                start = int(cols[1])
                end = int(cols[2])
                threshold = int(cols[4])
                length = end - start
                if threshold >= 10:
                    cov10 += length
                if threshold >= 30:
                    cov30 += length
            except (ValueError, IndexError):
                continue
    perc10 = 100 * cov10 / bed_total_bases
    perc30 = 100 * cov30 / bed_total_bases
    return perc10, perc30

def calculate_coverage() -> Tuple[float, float, float]:
    """Calcula estatísticas de cobertura"""
    logger.info("Calculando estatísticas de cobertura")
    
    # Executa mosdepth
    mosdepth_cmd = [
        "mosdepth",
        "--fasta", str(Config.FASTA),
        "--by", str(Config.BED),
        "--thresholds", "1,10,30",
        str(Config.RESULTS_DIR / "coverage"),
        str(Config.CRAM)
    ]
    run_command(mosdepth_cmd, "mosdepth para cálculo de cobertura")
    
    # Processa resultados
    summary_file = Config.RESULTS_DIR / "coverage.mosdepth.summary.txt"
    thresholds_file = Config.RESULTS_DIR / "coverage.thresholds.bed.gz"
    
    # Funções auxiliares (como as que você já tem)
    prof_media = ler_profundidade_media(summary_file)
    total_bases_bed = calcular_bases_bed(Config.BED)
    perc10, perc30 = calcular_percentuais(thresholds_file, total_bases_bed)
    
    return prof_media, perc10, perc30

def infer_sex() -> str:
    """Infere sexo genético baseado na cobertura de X e Y"""
    logger.info("Inferindo sexo genético")
    
    # Cria BEDs temporários para X e Y
    chr_x_bed = Config.RESULTS_DIR / "chrX.bed"
    chr_y_bed = Config.RESULTS_DIR / "chrY.bed"
    
    with open(chr_x_bed, "w") as f:
        f.write("chrX\t0\t156040895\n")
    with open(chr_y_bed, "w") as f:
        f.write("chrY\t0\t57227415\n")
    
    # Executa mosdepth para X e Y
    for chrom, bed_file in [("X", chr_x_bed), ("Y", chr_y_bed)]:
        cmd = [
            "mosdepth",
            "--fasta", str(Config.FASTA),
            "--by", str(bed_file),
            str(Config.RESULTS_DIR / f"chr{chrom}"),
            str(Config.CRAM)
        ]
        run_command(cmd, f"mosdepth para cromossomo {chrom}")
    
    # Processa resultados
    summary_x = Config.RESULTS_DIR / "chrX.mosdepth.summary.txt"
    summary_y = Config.RESULTS_DIR / "chrY.mosdepth.summary.txt"
    
    prof_x = ler_profundidade_media(summary_x)
    logger.info(f"Profundidade média X: {prof_x}")
    
    prof_y = ler_profundidade_media(summary_y)
    logger.info(f"Profundidade média Y: {prof_y}")
    
    ratio = prof_y / prof_x if prof_x > 0 else 0
    
    if ratio < 0.1:
        return "Feminino (XX)"
    elif 0.3 <= ratio <= 0.7:
        return "Masculino (XY)"
    else:
        return "Indeterminado"

def parse_contamination_results(output_prefix: Path) -> float:
    """Analisa o arquivo de saída do VerifyBamID2 para extrair o valor FREEMIX"""
    result_file = output_prefix.with_suffix(".selfSM")
    
    if not result_file.exists():
        logger.error(f"Arquivo de resultados não encontrado: {result_file}")
        return float('nan')
    
    try:
        with open(result_file) as f:
            # Pula o cabeçalho
            next(f)
            # Lê a linha de dados
            line = next(f)
            cols = line.strip().split('\t')
            
            # O índice 7 corresponde à coluna FREEMIX
            freemix = float(cols[7])
            logger.info(f"Contaminação estimada (FREEMIX): {freemix:.4f}")
            
            return freemix
            
    except Exception as e:
        logger.error(f"Erro ao processar arquivo de resultados: {str(e)}")
        return float('nan')
    
def estimate_contamination_fallback(dat_version: str) -> float:
    """Método alternativo usando parâmetros individuais"""
    resource_dir = Config.REFERENCE_DIR / "verifybamid2"
    required_files = Config.VERIFYBAMID_DAT_OPTIONS[dat_version]['files']
    
    try:
        ud_file = resource_dir / required_files['UD']
        bed_file = resource_dir / required_files['bed']
        mu_file = resource_dir / required_files['mu']
        
        output_prefix = Config.RESULTS_DIR / "contamination_fallback"
        cmd = [
            "verifybamid2",
            "--UDPath", str(ud_file),
            "--BedPath", str(bed_file),
            "--MeanPath", str(mu_file),
            "--Reference", str(Config.FASTA),
            "--BamFile", str(Config.CRAM),
            "--Output", str(output_prefix),
            "--NumThread", "4",
        ]
        
        run_command(cmd, "VerifyBamID2 (fallback)")
        return parse_contamination_results(output_prefix)
        
    except Exception as e:
        logger.error(f"Falha no método alternativo: {str(e)}")
        return float('nan')

def estimate_contamination(dat_version: str = '100k') -> float:
    """Estima contaminação usando VerifyBamID2 com método recomendado"""

    resource_dir = Path(Config.REFERENCE_DIR) / "verifybamid2"
    logger.debug(f"Listando arquivos em {resource_dir}:")
    logger.debug(f"resource_dir absolute: {resource_dir.resolve()}")

    try:
        files_in_dir = os.listdir(resource_dir)
    except FileNotFoundError:
        logger.error(f"Pasta de recursos não encontrada: {resource_dir}")
        return float('nan')

    for f in files_in_dir:
        logger.debug(f"  - {f}")

    base_filename = f"1000g.phase3.{dat_version}.b38.vcf.gz.dat"
    # Monta a lista dos arquivos obrigatórios para VerifyBamID2
    required_exts = ['.UD', '.bed', '.mu']
    missing_files = []
    for ext in required_exts:
        filepath = resource_dir / (base_filename + ext)
        if not filepath.exists():
            missing_files.append(str(filepath))

    if missing_files:
        logger.error(f"Arquivos do VerifyBamID2 faltando: {', '.join(missing_files)}")
        logger.info("Execute primeiro: python download_references.py --verifybamid")
        return float('nan')

    svd_prefix = resource_dir / base_filename
    output_prefix = Path(Config.RESULTS_DIR) / "contamination"

    cmd = [
        "verifybamid2",
        "--SVDPrefix", str(svd_prefix),
        "--Reference", str(Config.FASTA),
        "--BamFile", str(Config.CRAM),
        "--Output", str(output_prefix),
        "--NumThread", "4",
        "--Epsilon", "1e-8",
    ]

    try:
        run_command(cmd, "VerifyBamID2")

        result_file = output_prefix.with_suffix(".selfSM")
        if not result_file.exists():
            logger.error("Arquivo de resultados não foi gerado")
            return float('nan')

        return parse_contamination_results(output_prefix)

    except subprocess.CalledProcessError as e:
        logger.error(f"Erro no VerifyBamID2: {e.stderr}")
        logger.info("Tentando método alternativo com parâmetros individuais...")
        return estimate_contamination_fallback(dat_version)

def generate_report(coverage_stats: Tuple, sex: str, contamination: float) -> None:
    """Gera relatório final"""
    prof_media, perc10, perc30 = coverage_stats
    
    report = f"""
=== Relatório de Controle de Qualidade ===

1. Cobertura:
   - Profundidade média: {prof_media:.2f}x
   - % do exoma coberto ≥10x: {perc10:.2f}%
   - % do exoma coberto ≥30x: {perc30:.2f}%

2. Sexo genético: {sex}

3. Contaminação:
   - FREEMIX: {contamination:.4f}
   - Interpretação: {'✅ Baixa contaminação' if contamination < 0.03 else '⚠️ Possível contaminação'}
"""
    report_file = Config.RESULTS_DIR / "relatorio_final.txt"
    with open(report_file, "w") as f:
        f.write(report)
    
    logger.info(f"Relatório gerado em: {report_file}")

def main():
    try:        
        setup_directories()
        
        # Verifica arquivos de entrada
        check_file_exists(Config.CRAM, "Arquivo CRAM")
        check_file_exists(Config.BED, "Arquivo BED")
        check_file_exists(Config.FASTA, "Arquivo FASTA de referência")
        
        # Executa análises
        coverage_stats = calculate_coverage()
        sex = infer_sex()
        contamination = estimate_contamination()
        
        # Gera relatório
        generate_report(coverage_stats, sex, contamination)
        
        logger.info("Pipeline concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()