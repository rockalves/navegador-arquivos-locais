import os
from flask import Flask, render_template, send_from_directory, request, abort
import configparser
from datetime import datetime

app = Flask(__name__)

# Configurações
config = configparser.ConfigParser()
config.read('config.conf')
diretorio_raiz = config['DEFAULT']['diretorio_raiz']

def tamanho_legivel(tamanho_bytes):
    """Converte bytes para um formato legível (GB)."""
    tamanho_gb = tamanho_bytes / (1024 ** 3)
    return f"{tamanho_gb:.2f} GB"

def data_modificacao(caminho):
    """Retorna a data de modificação de um arquivo/diretório."""
    timestamp = os.path.getmtime(caminho)
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/', defaults={'caminho': ''})
@app.route('/<path:caminho>')
def index(caminho):
    caminho_absoluto = os.path.join(diretorio_raiz, caminho)
    if not os.path.exists(caminho_absoluto):
        abort(404)

    itens = []
    for item in os.listdir(caminho_absoluto):
        item_absoluto = os.path.join(caminho_absoluto, item)
        tamanho = tamanho_legivel(os.path.getsize(item_absoluto)) if os.path.isfile(item_absoluto) else None
        data = data_modificacao(item_absoluto)
        itens.append({
            'nome': item,
            'caminho': os.path.join(caminho, item),
            'diretorio': os.path.isdir(item_absoluto),
            'tamanho': tamanho,
            'data': data,
        })

    caminho_superior = os.path.dirname(caminho)
    if caminho_superior == '.':
        caminho_superior = ''

    return render_template('index.html', itens=itens, caminho_superior=caminho_superior)

@app.route('/download/<path:caminho>')
def download(caminho):
    caminho_absoluto = os.path.join(diretorio_raiz, caminho)
    if not os.path.isfile(caminho_absoluto):
        abort(404)
    diretorio_pai, nome_arquivo = os.path.split(caminho_absoluto)
    return send_from_directory(diretorio_pai, nome_arquivo, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
