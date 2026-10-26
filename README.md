# Extrator e divisor de páginas PDF

Aplicação Gradio que recebe um PDF, extrai a capa e a contracapa e divide as
páginas internas em imagens PNG, entregues em um arquivo ZIP.

## Processamento e memória

Para manter o uso de memória previsível no Render, cada imagem tem um limite de
4 milhões de pixels. Páginas que excederem esse limite são renderizadas em uma
escala menor; a interface mostra o progresso por página.

## Executar localmente no macOS

No Terminal, entre na pasta do projeto:

```bash
cd ~/Documents/AndClaw/PDF
```

Crie e ative um ambiente virtual (a ativação pode ser repetida em novos
terminais):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inicie a aplicação:

```bash
python app.py
```

Abra [http://localhost:7860](http://localhost:7860) no navegador, selecione um
PDF e clique em **Extrair e Dividir Imagens**. O ZIP resultante será oferecido
para download na própria página.

Para encerrar, volte ao Terminal e pressione `Ctrl+C`. Para reativar o ambiente
virtual depois, use `cd ~/Documents/AndClaw/PDF` e `source .venv/bin/activate`.

## Render

Configure o comando de inicialização do serviço como `python app.py`. A porta é
lida da variável de ambiente `PORT`; localmente, o padrão é `7860`.
