import fitz
from pathlib import Path

# Caminhos relativos ao workspace
pdf_path = Path("PDF") / "Abelha Rainha - Campanha 04-26.pdf"
# pasta de saída absoluta conforme solicitado
pasta_saida = Path(r"C:\Users\anderson.silva\Pictures\Imagens Visual Studio")

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF não encontrado: {pdf_path.resolve()}")

pasta_saida.mkdir(parents=True, exist_ok=True)


def salvar_imagem_com_nome(pixmap, caminho):
    caminho_str = str(caminho)
    pixmap.save(caminho_str)


def format_num_for_filename(n):
    # pad to 2 digits for numbers < 100, keep 3-digit numbers as-is
    if n >= 100:
        return str(n)
    return str(n).zfill(2)


documento = fitz.open(pdf_path)
total_paginas = len(documento)
nao_encontrados = []
counter = 1
for numero_pagina, pagina in enumerate(documento, start=1):
    largura = pagina.rect.width
    altura = pagina.rect.height
    meio = largura / 2
    matriz = fitz.Matrix(2, 2)

    # primeira página: capa (única) -> nome sequential
    if numero_pagina == 1:
        nome = format_num_for_filename(counter) + ".png"
        pix = pagina.get_pixmap(matrix=matriz)
        caminho_arquivo = pasta_saida / nome
        if caminho_arquivo.exists():
            caminho_arquivo = pasta_saida / f"{caminho_arquivo.stem}_1{caminho_arquivo.suffix}"
        salvar_imagem_com_nome(pix, caminho_arquivo)
        counter += 1
        continue

    # última página: contra-capa (única) -> nome sequential (ensure it's last)
    if numero_pagina == total_paginas:
        nome = format_num_for_filename(counter) + ".png"
        pix = pagina.get_pixmap(matrix=matriz)
        caminho_arquivo = pasta_saida / nome
        if caminho_arquivo.exists():
            caminho_arquivo = pasta_saida / f"{caminho_arquivo.stem}_1{caminho_arquivo.suffix}"
        salvar_imagem_com_nome(pix, caminho_arquivo)
        counter += 1
        continue

    # páginas internas: dividir em dois (esquerdo, direito) e nomear sequencialmente
    clip_esq = fitz.Rect(0, 0, meio, altura)
    pix_esq = pagina.get_pixmap(matrix=matriz, clip=clip_esq)
    nome_esq = format_num_for_filename(counter) + ".png"
    caminho_esq = pasta_saida / nome_esq
    if caminho_esq.exists():
        caminho_esq = pasta_saida / f"{caminho_esq.stem}_1{caminho_esq.suffix}"
    salvar_imagem_com_nome(pix_esq, caminho_esq)
    counter += 1

    clip_dir = fitz.Rect(meio, 0, largura, altura)
    pix_dir = pagina.get_pixmap(matrix=matriz, clip=clip_dir)
    nome_dir = format_num_for_filename(counter) + ".png"
    caminho_dir = pasta_saida / nome_dir
    if caminho_dir.exists():
        caminho_dir = pasta_saida / f"{caminho_dir.stem}_1{caminho_dir.suffix}"
    salvar_imagem_com_nome(pix_dir, caminho_dir)
    counter += 1

print(f"Processo concluído. Pasta de saída: {pasta_saida.resolve()}")
if nao_encontrados:
    print("Atenção: não foi possível extrair número de rodapé para as páginas:")
    print(nao_encontrados)
