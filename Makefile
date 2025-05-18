.PHONY: all run clean docker-build docker-run data-and-references

# Caminho absoluto do projeto WSL (ajuste se necessário)
PROJECT_ROOT := /home/$(USER)/projetos_python/desafio_bionfomatica

all: data-and-references docker-build docker-run

data-and-references:
	python3 download_data_and_references.py

clean:
	rm -rf results/*
	rm -f data/*.bam data/*.bai

docker-build:
	docker build -t bioinfo_pipeline .

docker-run:
	docker run --rm \
		-v $(PROJECT_ROOT)/data:/app/data \
		-v $(PROJECT_ROOT)/results:/app/results \
		bioinfo_pipeline

