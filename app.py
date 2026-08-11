import fitz
import tempfile
import zipfile
import os
from pathlib import Path
import gradio as gr

def processar_pdf(pdf_file):
    if pdf_file is None:
        return None, "Por favor, envie um arquivo PDF."
    
    # Criar diretório temporário para extração
    temp_dir = tempfile.mkdtemp()
    pasta_saida = Path(temp_dir)
    
    pdf_path = Path(pdf_file.name)
    documento = fitz.open(pdf_path)
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
        # O Render Free tem apenas 0.1 vCPU e 512MB RAM.
        # A matriz (2,2) exige MUITA memória e CPU. Reduzimos para (1.5, 1.5) para evitar crash (Erro 502) e lentidão extrema na nuvem.
        matriz = fitz.Matrix(1.5, 1.5)

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
    
    # Criar arquivo ZIP com todas as imagens geradas
    zip_path = pasta_saida / "imagens_extraidas.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in pasta_saida.glob("*.png"):
            zipf.write(file, arcname=file.name)
            
    mensagem = f"Sucesso! {counter - 1} imagens foram extraídas e compactadas."
    return str(zip_path), mensagem

with gr.Blocks(title="Extrator de Imagens PDF - AndersonIM") as demo:
    gr.Markdown("# 📄 Extrator & Divisor de Páginas de PDF")
    gr.Markdown("Faça upload do seu PDF do catálogo para extrair a capa, contra-capa e dividir as páginas duplas automaticamente.")
    
    with gr.Row():
        pdf_input = gr.File(label="Selecione o arquivo PDF", file_types=[".pdf"])
    
    btn_processar = gr.Button("✂️ Extrair e Dividir Imagens", variant="primary", interactive=False)
    
    status_output = gr.Textbox(label="Status do Processamento", interactive=False)
    zip_output = gr.File(label="Baixar Imagens em ZIP (.zip)")

    # Habilitar o botão apenas quando o arquivo PDF for enviado
    pdf_input.change(
        fn=lambda x: gr.update(interactive=bool(x)), 
        inputs=[pdf_input], 
        outputs=[btn_processar]
    )
    
    # Desabilitar botão durante o processamento para evitar cliques duplos
    btn_processar.click(
        fn=lambda: gr.update(interactive=False),
        inputs=[],
        outputs=[btn_processar]
    ).then(
        fn=processar_pdf,
        inputs=[pdf_input],
        outputs=[zip_output, status_output]
    ).then(
        fn=lambda: gr.update(interactive=True),
        inputs=[],
        outputs=[btn_processar]
    )

if __name__ == "__main__":
    # O Render fornece a porta correta na variável de ambiente PORT.
    porta = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=porta)
