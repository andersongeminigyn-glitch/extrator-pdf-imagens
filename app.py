import pymupdf
import tempfile
import zipfile
import os
import gc
from pathlib import Path
import gradio as gr


def processar_pdf(pdf_file: str | None):
    if pdf_file is None:
        return None, "Por favor, envie um arquivo PDF."

    temp_dir = tempfile.mkdtemp()
    pasta_saida = Path(temp_dir)
    pdf_path = Path(pdf_file)
    counter = 1

    def format_num_for_filename(n):
        if n >= 100:
            return str(n)
        return str(n).zfill(2)

    def proximo_caminho():
        nonlocal counter
        caminho = pasta_saida / f"{format_num_for_filename(counter)}.png"
        counter += 1
        if caminho.exists():
            caminho = caminho.with_name(f"{caminho.stem}_1{caminho.suffix}")
        return caminho

    matriz = pymupdf.Matrix(1.8, 1.8)

    with pymupdf.open(pdf_path) as documento:
        total_paginas = len(documento)
        for numero_pagina, pagina in enumerate(documento, start=1):
            if numero_pagina == 1 or numero_pagina == total_paginas:
                pixmap = pagina.get_pixmap(matrix=matriz, alpha=False, annots=False)
                pixmap.save(str(proximo_caminho()))
                del pixmap
                gc.collect()
                continue

            largura = pagina.rect.width
            altura = pagina.rect.height
            meio = largura / 2

            clip_esq = pymupdf.Rect(0, 0, meio, altura)
            pix_esq = pagina.get_pixmap(matrix=matriz, clip=clip_esq, alpha=False, annots=False)
            pix_esq.save(str(proximo_caminho()))
            del pix_esq
            gc.collect()

            clip_dir = pymupdf.Rect(meio, 0, largura, altura)
            pix_dir = pagina.get_pixmap(matrix=matriz, clip=clip_dir, alpha=False, annots=False)
            pix_dir.save(str(proximo_caminho()))
            del pix_dir
            gc.collect()

    zip_path = pasta_saida / "imagens_extraidas.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zipf:
        for file in sorted(pasta_saida.glob("*.png"), key=lambda f: f.name):
            zipf.write(file, arcname=file.name)

    mensagem = f"Sucesso! {counter - 1} imagens foram extraídas e compactadas."
    gc.collect()
    return str(zip_path), mensagem

with gr.Blocks(title="Extrator de Imagens PDF - AndersonIM") as demo:
    gr.Markdown("# 📄 Extrator & Divisor de Páginas de PDF")
    gr.Markdown("Faça upload do seu PDF do catálogo para extrair a capa, contra-capa e dividir as páginas duplas automaticamente.")
    
    with gr.Row():
        pdf_input = gr.File(
            label="Selecione o arquivo PDF",
            file_types=[".pdf"],
            type="filepath",
        )
    
    btn_processar = gr.Button("✂️ Extrair e Dividir Imagens", variant="primary", interactive=False)
    
    status_output = gr.Textbox(label="Status do Processamento", interactive=False)
    zip_output = gr.File(label="Baixar Imagens em ZIP (.zip)")

    # Habilitar o botão apenas quando o arquivo PDF for enviado
    pdf_input.change(
        fn=lambda x: gr.update(interactive=bool(x)),
        inputs=[pdf_input], 
        outputs=[btn_processar]
    )
    
    btn_processar.click(
        fn=processar_pdf,
        inputs=[pdf_input],
        outputs=[zip_output, status_output],
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 7860))
    demo.queue(max_size=10)
    demo.launch(server_name="0.0.0.0", server_port=porta, show_error=True, max_threads=1)
