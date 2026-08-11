import fitz
import tempfile
import zipfile
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Extrator de Imagens PDF", page_icon="📄", layout="centered")

st.title("📄 Extrator & Divisor de Páginas de PDF")
st.markdown("Faça upload do seu PDF do catálogo para extrair a capa, contra-capa e dividir as páginas duplas automaticamente.")

uploaded_file = st.file_uploader("Selecione o arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    if st.button("✂️ Extrair e Dividir Imagens", type="primary"):
        with st.spinner("Processando páginas do PDF... Aguarde!"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_pdf_path = Path(tmp_file.name)
            
            temp_dir = tempfile.mkdtemp()
            pasta_saida = Path(temp_dir)
            
            documento = fitz.open(tmp_pdf_path)
            total_paginas = len(documento)
            counter = 1
            
            def format_num_for_filename(n):
                if n >= 100:
                    return str(n)
                return str(n).zfill(2)

            def salvar_imagem_com_nome(pixmap, caminho):
                pixmap.save(str(caminho))

            for numero_pagina, pagina in enumerate(documento, start=1):
                largura = pagina.rect.width
                altura = pagina.rect.height
                meio = largura / 2
                matriz = fitz.Matrix(2, 2)

                # Capa (primeira página)
                if numero_pagina == 1:
                    nome = format_num_for_filename(counter) + ".png"
                    pix = pagina.get_pixmap(matrix=matriz)
                    caminho_arquivo = pasta_saida / nome
                    if caminho_arquivo.exists():
                        caminho_arquivo = pasta_saida / f"{caminho_arquivo.stem}_1{caminho_arquivo.suffix}"
                    salvar_imagem_com_nome(pix, caminho_arquivo)
                    counter += 1
                    continue

                # Contra-capa (última página)
                if numero_pagina == total_paginas:
                    nome = format_num_for_filename(counter) + ".png"
                    pix = pagina.get_pixmap(matrix=matriz)
                    caminho_arquivo = pasta_saida / nome
                    if caminho_arquivo.exists():
                        caminho_arquivo = pasta_saida / f"{caminho_arquivo.stem}_1{caminho_arquivo.suffix}"
                    salvar_imagem_com_nome(pix, caminho_arquivo)
                    counter += 1
                    continue

                # Páginas internas (esquerda e direita)
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

            documento.close()
            
            zip_path = pasta_saida / "imagens_extraidas.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in pasta_saida.glob("*.png"):
                    zipf.write(file, arcname=file.name)
            
            with open(zip_path, "rb") as fp:
                zip_bytes = fp.read()

            st.success(f"Sucesso! {counter - 1} imagens foram extraídas e compactadas.")
            st.download_button(
                label="⬇️ Baixar Imagens em ZIP (.zip)",
                data=zip_bytes,
                file_name="imagens_extraidas.zip",
                mime="application/zip",
                type="primary"
            )
