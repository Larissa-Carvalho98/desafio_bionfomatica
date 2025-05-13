# DESAFIO BIOINFORMÁTICA

# 🧬 Pipeline de Bioinformática

Este pipeline foi desenvolvido para realizar análises de cobertura em regiões exônicas, inferência do sexo genético, estimativa de contaminação e geração de relatórios automatizados com base em dados de sequenciamento no formato CRAM.

## 🛠️ Pré-requisitos

### 🧪 Ativando o Conda manualmente (caso necessário)

Caso o Conda não esteja ativando automaticamente no seu terminal, inicialize-o manualmente com o comando abaixo (supondo que o Miniconda está instalado em `~/miniconda3`):

```bash
source ~/miniconda3/etc/profile.d/conda.sh

Depois disso, verifique a versão e ative o ambiente:

conda --version
conda activate bioinfo_env

### 🔧 Dependências

| Ferramenta   | Versão exata | Instalação Conda                                 |
|--------------|--------------|--------------------------------------------------|
| `samtools`   | 1.21         | `conda install -c bioconda samtools=1.21`        |
| `mosdepth`   | 0.3.10       | `conda install -c bioconda mosdepth=0.3.10`      |
| `Python`     | ≥3.8         | Incluído no ambiente Conda                       |
| `htslib`     | 1.21         | `conda install -c bioconda htslib=1.21`          |
| `libdeflate` | 1.23         | Instalado como dependência de `htslib`           |
| `openssl`    | 3.5.0        | `conda install -c conda-forge openssl=3.5.0`     |
| `numpy`      | 2.2.5        | `conda install numpy=2.2.5`                      |

## ✅ Requisitos do Projeto

- Sistema operacional: Linux
- Linguagens: Bash, Python
- Automatização via Bash script / Snakemake / Makefile 

## 📁 Estrutura do Projeto

project/
├── data/         # Dados brutos (CRAM, CRAI, BED)
├── scripts/      # Scripts do pipeline
├── results/      # Saídas e análises
└── pipeline/     # Arquivos de automação (ex: Snakefile, Makefile)

### 📁 Pipeline passo a passo

#### 1. Preparação do Ambiente

* Organização do projeto em pastas, separando dados brutos, scripts, resultados e relatórios.
* Instalação das ferramentas necessárias: `samtools`, `bedtools`, `mosdepth`
* Ativação de ambiente Conda.   

#### 2. Verificação das Integridades do Arquivo (hashes)

* md5sum NA06994*.cram
* md5sum NA06994*.crai
* md5sum hg38_exome_v2.0.2_targets_sorted_validated.re_annoted.bed

#### 3. Conversão do Arquivo CRAM

* A conversão do arquivo CRAM não foi necessária, pois o pipeline foi configurado para utilizar diretamente o formato CRAM nas análises.

#### 4.Calcular a Cobertura exômica

* Para calcular a cobertura nas regiões alvo do exoma, foi utilizado o Mosdepth

mosdepth --by hg38_exome_v2.0.2_targets_sorted_validated.re_annoted.bed sample NA06994.cram


#### 5.Inferência do sexo genético

* 📦 Ferramenta recomendada:samtools idxstats
* Feminino (XX): cobertura alta no X, ~0 no Y
* Masculino (XY): cobertura similar entre X e Y

#### 6.Estimativa de contaminação

* 📦 Ferramenta sugerida: VerifyBamID

verifyBamID --bam NA06994.cram --vcf ref.vcf.gz --out NA06994_verify

#### ✅ Conclusão

* Este pipeline oferece uma abordagem prática e eficiente para análises básicas em dados de sequenciamento, com foco em cobertura exômica, inferência do sexo genético e estimativa de contaminação. Utilizando ferramentas amplamente reconhecidas, ele permite obter resultados confiáveis de forma automatizada e organizada.








