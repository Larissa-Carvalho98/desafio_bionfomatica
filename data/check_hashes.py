import hashlib

def md5sum(filename):
    """Calcula o hash MD5 de um arquivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

def verificar_arquivos():
    # Mapeia os arquivos e os hashes esperados
    arquivos = {
        "NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram": "3d8d8dc27d85ceaf0daefa493b8bd660",
        "NA06994.alt_bwamem_GRCh38DH.20150826.CEU.exome.cram.crai": "15a6576f46f51c37299fc004ed47fcd9",
        "hg38_exome_v2.0.2_targets_sorted_validated.re_annotated.bed": "c3a7cea67f992e0412db4b596730d276"
    }

    print("🔍 Verificando integridade dos arquivos...\n")

    for arquivo, hash_esperado in arquivos.items():
        print(f"📁 Arquivo: {arquivo}")
        hash_calculado = md5sum(arquivo)

        if hash_calculado is None:
            print("  ❌ Arquivo não encontrado.\n")
        elif hash_calculado == hash_esperado:
            print("  ✅ Hash válido.\n")
        else:
            print("  ❌ Hash inválido!")
            print(f"     Esperado: {hash_esperado}")
            print(f"     Obtido:   {hash_calculado}\n")

if __name__ == "__main__":
    verificar_arquivos()
