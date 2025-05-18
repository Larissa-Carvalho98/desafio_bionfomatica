# DESAFIO BIOINFORMÁTICA

## 👤 Autor

- Nome: Larissa Vieira de Carvalho
- E-mail: larissav646@gmail.com
- GitHub: [Larissa-Carvalho98](https://github.com/Larissa-Carvalho98)
- LinkedIn: [Larissa Vieira de Carvalho](linkedin.com/in/larissa-vieira-de-carvalho-9b9b4b155)

## 🧬 Pipeline de Bioinformática

Este projeto é um pipeline de bioinformática desenvolvido para realizar análises de cobertura em regiões exônicas, inferência do sexo genético, estimativa de contaminação e geração de relatórios automatizados com base em dados de sequenciamento no formato CRAM.

---

## 📁 Estrutura do Projeto

```
project/
├── data/         # Dados brutos (CRAM, CRAI, BED)
├── results/      # Saídas e análises
├── environment.yml
├── Makefile
├── Dockerfile
├── config.py
├── download_data_and_references.py
├── pipeline.py
└── README.md
```

- **data/**: Armazena os arquivos de entrada necessários para a análise.
- **results/**: Guarda os resultados gerados pelo pipeline.
- **environment.yml**: Define o ambiente Conda e as dependências do projeto.
- **Makefile**: Comandos para executar, limpar e rodar o pipeline via Docker.
- **Dockerfile**: Imagem Docker para ambiente reprodutível.
- **config.py**: Configurações de caminhos e opções do projeto.
- **download_data_and_references.py**: Script para baixar dados e referências.
- **pipeline.py**: Script principal do pipeline.

---

## 🛠️ Pré-requisitos

- **Sistema operacional:** Linux
- **Linguagens:** Bash, Python
- **Automatização:** Bash script / Makefile

### 🔧 Dependências Principais

| Ferramenta     | Versão exata | Instalação Conda                               |
| -------------- | ------------ | ---------------------------------------------- |
| `samtools`     | 1.21         | `conda install -c bioconda samtools=1.21`      |
| `mosdepth`     | 0.3.10       | `conda install -c bioconda mosdepth=0.3.10`    |
| `VerifyBamID2` | 2.0.1        | `conda install -c bioconda verifybamid2=2.0.1` |
| `Python`       | ≥3.8         | Incluído no ambiente Conda                     |

Todas as dependências podem ser instaladas via Conda usando o arquivo `environment.yml`.

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone <repository-url>
cd desafio_bionfomatica
```

Use o Makefile:

### 2. Executar o pipeline em um ambiente Conda em Docker

```bash
make all
```

O alvo `all` executa: download dos dados, build da imagem Docker e execução do pipeline no container.

---

## 📄 Pipeline passo a passo

### 1. Preparação do Ambiente

- Organização do projeto em pastas, separando dados brutos, scripts, resultados e relatórios.
- Instalação das ferramentas necessárias: `samtools`, `mosdepth`, `VerifyBamID2`.
- Ativação do ambiente Conda.

### 2. Verificação das Integridades dos Arquivos

- `md5sum NA06994*.cram`
- `md5sum NA06994*.crai`
- `md5sum hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed`

### 3. Conversão do Arquivo CRAM

- Não é necessária, pois o pipeline utiliza diretamente o formato CRAM.

### 4. Cálculo da Cobertura Exômica

- Utiliza o Mosdepth para calcular a cobertura nas regiões alvo do exoma:
  ```bash
  mosdepth --by hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed sample NA06994.cram
  ```

### 5. Inferência do Sexo Genético

- Ferramenta recomendada: `samtools idxstats` ou Mosdepth em regiões X/Y.
- Feminino (XX): cobertura alta no X, ~0 no Y.
- Masculino (XY): cobertura similar entre X e Y.

### 6. Estimativa de Contaminação

- Ferramenta sugerida: `VerifyBamID2`
  ```bash
  verifybamid2 --bam NA06994.cram --vcf ref.vcf.gz --out NA06994_verify
  ```

### 7. Geração de Relatório

- O pipeline gera um relatório final em `results/relatorio_final.txt` com as principais métricas de qualidade.

---

## 📦 Arquivos de Dados

No diretório `data/` estão os arquivos de dados utilizados no pipeline:

- `NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram`
- `NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram.crai`
- `hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed`

Para baixar automaticamente, use:

```bash
python download_data_and_references.py
```

Ou manualmente:

```bash
wget -P data/ https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/data/CEU/NA06994/exome_alignment/NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram
wget -P data/ https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/data/CEU/NA06994/exome_alignment/NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram.crai
wget -P data/ https://www.twistbioscience.com/sites/default/files/resources/2022-12/hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed
```

---

## 📚 Arquivos de Referência

O pipeline requer arquivos adicionais para a estimativa de contaminação:

- **Genoma de referência GRCh38**:  
  `Homo_sapiens_assembly38.fasta`  
  Disponível em:  
  https://storage.googleapis.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta

- **Arquivos do VerifyBamID2**:  
  Baixados automaticamente pelo script `download_data_and_references.py`.

---

## 📝 Logging e Relatórios

- Todas as atividades do pipeline são registradas em `results/pipeline.log`.
- O relatório final é salvo em `results/relatorio_final.txt`.

---

## 📊 Interpretação dos Resultados (`relatorio_final.txt`)

O arquivo `results/relatorio_final.txt` apresenta um resumo das principais métricas de qualidade obtidas pelo pipeline.

1. **Cobertura**

   - **Profundidade média:** Indica o número médio de vezes que cada base das regiões alvo foi sequenciada. Valores acima de 30x são considerados excelentes para exoma.
   - **% do exoma coberto ≥10x e ≥30x:** Mostram a proporção das regiões alvo que atingiram pelo menos 10 ou 30 leituras. Altos percentuais (>95%) garantem confiabilidade na análise de variantes.

2. **Sexo genético**

   - Determinado a partir da razão de cobertura dos cromossomos X e Y. "Masculino (XY)" indica presença de cobertura significativa no Y; "Feminino (XX)" indica ausência ou cobertura muito baixa no Y.

3. **Contaminação**
   - **FREEMIX:** Valor estimado pelo VerifyBamID2. Valores próximos de zero indicam baixa contaminação. O pipeline também fornece uma interpretação automática (✅ Baixa contaminação).

Essas métricas são essenciais para garantir a qualidade dos dados antes de análises genéticas mais avançadas.

---

## ℹ️ Observações

- O Makefile automatiza todo o fluxo: download dos dados, build da imagem Docker e execução do pipeline.

---
