import subprocess
from pathlib import Path
import os
import gzip

# Define caminhos
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
REFERENCE_DIR = DATA_DIR / "reference"
CRAM = DATA_DIR / "NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram"
BED = DATA_DIR / "hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed"
PREFIX = RESULTS_DIR / "NA06994"
FASTA = REFERENCE_DIR / "Homo_sapiens_assembly38.fasta"

# Cria pastas se não existirem
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
REFERENCE_DIR.mkdir(exist_ok=True)

# ---------- Criar arquivos BED para cromossomos X e Y ----------
CHR_X_BED = DATA_DIR / "chrX.bed"
CHR_Y_BED = DATA_DIR / "chrY.bed"

# Configura variável de ambiente REF_PATH
env = os.environ.copy()
env["REF_PATH"] = str(FASTA)

# if not CHR_X_BED.exists():
#     with open(CHR_X_BED, "w") as f:
#         f.write("chrX\t0\t156040895\n")  # Tamanho aproximado do chrX

# if not CHR_Y_BED.exists():
#     with open(CHR_Y_BED, "w") as f:
#         f.write("chrY\t0\t57227415\n")  # Tamanho aproximado do chrY

# # ---------- Funções ----------

# # Executa mosdepth para arquivos BED específicos
# def run_mosdepth_chr(bed_file, cram_file, prefix):
#     cmd = [
#         "mosdepth",
#         "--fasta", str(FASTA),  # <--- adicione esta linha
#         "--by", str(bed_file),
#         str(prefix),
#         str(cram_file)
#     ]
#     try:
#         subprocess.run(cmd, check=True)
#         print(f"mosdepth para {prefix.name} executado com sucesso.")
#     except subprocess.CalledProcessError as e:
#         print(f"Erro ao rodar mosdepth para {prefix.name}: {e}")
#         exit(1)

# # Lê profundidade média de um arquivo summary.txt
# def ler_profundidade_media(summary_file):
#     with open(summary_file) as f:
#         for line in f:
#             if line.startswith("total_region"):
#                 cols = line.strip().split()
#                 return float(cols[3])  # profundidade média
#     return 0.0

# # Conta o número total de bases no BED
# def calcular_bases_bed(bed_file):
#     total = 0
#     with open(bed_file) as f:
#         for line in f:
#             cols = line.strip().split()
#             total += int(cols[2]) - int(cols[1])
#     return total

# # Calcula percentuais ≥10x e ≥30x
# def calcular_percentuais(thresholds_file, bed_total_bases):
#     cov10 = 0
#     cov30 = 0
#     with gzip.open(thresholds_file, "rt") as f:
#         next(f)  # pula o cabeçalho
#         for line in f:
#             cols = line.strip().split()
#             if len(cols) < 5:
#                 continue
#             try:
#                 start = int(cols[1])
#                 end = int(cols[2])
#                 threshold = int(cols[4])
#                 length = end - start
#                 if threshold >= 10:
#                     cov10 += length
#                 if threshold >= 30:
#                     cov30 += length
#             except (ValueError, IndexError):
#                 continue
#     perc10 = 100 * cov10 / bed_total_bases
#     perc30 = 100 * cov30 / bed_total_bases
#     return perc10, perc30

# # Inferência do sexo genético com base nas coberturas X e Y
# def inferir_sexo(summary_x, summary_y):
#     prof_x = ler_profundidade_media(summary_x)
#     prof_y = ler_profundidade_media(summary_y)

#     print(f"\nCobertura cromossomo X: {prof_x:.2f}x")
#     print(f"Cobertura cromossomo Y: {prof_y:.2f}x")

#     if prof_y < 1.0:
#         sexo = "Provavelmente feminino (XX)"
#     elif abs(prof_x - prof_y) / max(prof_x, prof_y) < 0.5:
#         sexo = "Provavelmente masculino (XY)"
#     else:
#         sexo = "Indeterminado ou dados inconsistentes"

#     print(f"Inferência de sexo genético: {sexo}")

# # ---------- Executar pipeline principal ----------

# # Roda mosdepth principal (com thresholds)
# MOSDEPTH_PREFIX = str(PREFIX)
# MOSDEPTH_CMD = [
#     "mosdepth",
#     "--fasta", str(FASTA),  # <--- adicione esta linha
#     "--by", str(BED),
#     "--thresholds", "1,10,30",
#     MOSDEPTH_PREFIX,
#     str(CRAM)
# ]


# print("Executando mosdepth com thresholds...")
# subprocess.run(MOSDEPTH_CMD, check=True, env=env)

# # Resultados principais
# SUMMARY = RESULTS_DIR / "NA06994.mosdepth.summary.txt"
# THRESHOLDS = RESULTS_DIR / "NA06994.thresholds.bed.gz"

# print("Calculando estatísticas de cobertura...")
# prof_media = ler_profundidade_media(SUMMARY)
# total_bases_bed = calcular_bases_bed(BED)
# perc10, perc30 = calcular_percentuais(THRESHOLDS, total_bases_bed)

# print(f"\nResumo da cobertura nas regiões do BED:")
# print(f"- Profundidade média: {prof_media:.2f}x")
# print(f"- % de regiões com cobertura ≥10x: {perc10:.2f}%")
# print(f"- % de regiões com cobertura ≥30x: {perc30:.2f}%")

# # Roda mosdepth para cromossomos X e Y
# run_mosdepth_chr(CHR_X_BED, CRAM, RESULTS_DIR / "NA06994_chrX")
# run_mosdepth_chr(CHR_Y_BED, CRAM, RESULTS_DIR / "NA06994_chrY")

# # Inferência do sexo genético
# SUMMARY_X = RESULTS_DIR / "NA06994_chrX.mosdepth.summary.txt"
# SUMMARY_Y = RESULTS_DIR / "NA06994_chrY.mosdepth.summary.txt"
# inferir_sexo(SUMMARY_X, SUMMARY_Y)

# ---------- Estimativa de contaminação com VerifyBamID2 ----------

print("\nIniciando estimativa de contaminação com VerifyBamID2...")

BAM_FILE = RESULTS_DIR / "NA06994.bam"
BAM_INDEX = RESULTS_DIR / "NA06994.bam.bai"
VERIFYBAMID2_OUT = RESULTS_DIR / "verifybamid2_out"

# Converte CRAM para BAM se ainda não existir
if not BAM_FILE.exists():
    print("Convertendo CRAM para BAM...")
    subprocess.run([
        "samtools", "view", "-b", "-T", str(FASTA), "-o", str(BAM_FILE), str(CRAM)
    ], check=True)

# Indexa o BAM
if not BAM_INDEX.exists():
    print("Indexando BAM...")
    subprocess.run([
        "samtools", "index", str(BAM_FILE)
    ], check=True)

# Executa verifybamid2
print("Executando VerifyBamID2...")
subprocess.run([
    "verifybamid2",
    "--Reference", str(FASTA),
    "--BamFile", str(BAM_FILE),
    "--Output", str(VERIFYBAMID2_OUT),
    "--NumThread", "4"
], check=True)

# Lê FREEMIX da saída
FREEMIX_FILE = str(VERIFYBAMID2_OUT) + ".selfSM"
if os.path.exists(FREEMIX_FILE):
    with open(FREEMIX_FILE) as f:
        next(f)  # cabeçalho
        for line in f:
            cols = line.strip().split()
            freemix = float(cols[7])
            print(f"\nEstimativa de contaminação (FREEMIX): {freemix:.4f}")
            if freemix > 0.03:
                print("⚠️ Possível contaminação detectada!")
            else:
                print("✅ Sem sinais claros de contaminação.")
else:
    print("Arquivo de saída do VerifyBamID2 não encontrado.")
