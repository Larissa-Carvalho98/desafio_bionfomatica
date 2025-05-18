# filepath: /home/host/projetos_python/desafio_bionfomatica/Dockerfile
# Estágio de construção
FROM continuumio/miniconda3 AS builder

# Copia o arquivo environment.yml
COPY environment.yml .

# Cria o ambiente conda e instala as dependências
RUN conda env create -f environment.yml

# Estágio final
FROM continuumio/miniconda3

# Copia o ambiente conda do estágio de construção
COPY --from=builder /opt/conda /opt/conda

# Configura o ambiente
ENV PATH /opt/conda/bin:$PATH

# Define o diretório de trabalho
WORKDIR /app

# Copia o restante dos arquivos do projeto
COPY . .

# Ativa o ambiente e define o comando de entrada
ENTRYPOINT ["conda", "run", "-n", "bioinfo_env", "python", "pipeline.py"]