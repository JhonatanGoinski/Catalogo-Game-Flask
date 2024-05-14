from flask import render_template, request, redirect, session, flash, url_for, send_from_directory
from jogoteca import app, db
from models import Jogos
from helpers import recupera_imagem, deleta_arquivo, FormularioJogo
import time
# Rota do html onde apareceram todos os jogos cadastrados
@app.route('/')
def index():
    lista = Jogos.query.order_by(Jogos.id)
    return render_template('lista.html', titulo='Jogos', jogos=lista )
# FIM - Rota do html onde apareceram todos os jogos cadastrados

# Rota para formulario de adicionar novo jogo
@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioJogo()
    return render_template('novo.html', titulo='Novo Jogo', form=form)
# FIM - Rota para formulario de adicionar novo jogo


# Capturar informações inseridas na area html novo, para criação de novo jogo.
@app.route('/criar', methods=['POST'])
def criar():

    form = FormularioJogo(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('novo'))
    

    nome = form.nome.data
    categoria = form.categoria.data
    console = form.console.data
    
    jogo = Jogos.query.filter_by(nome=nome).first()
    if jogo:
        flash('Jogo já existente!')
        return redirect(url_for('index'))
    
    novo_jogo = Jogos(nome=nome, categoria=categoria, console=console)
    db.session.add(novo_jogo)
    db.session.commit()

    # Informando o diretorio de onde ficará guardado as imgs dos jogos
    upload_path = app.config['UPLOAD_PATH']
    arquivo = request.files['arquivo']
    timestamp = time.time()
    arquivo.save(f'{upload_path}/capa{novo_jogo.id}-{timestamp}.jpg')
    # FIM - Informando o diretorio de onde ficará guardado as imgs dos jogos

    return redirect(url_for('index'))
# FIM - Capturar informações inseridas na area html novo, para criação de novo jogo.

# Rota para formulario de editar
@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))
    jogo = Jogos.query.filter_by(id=id).first()
    form = FormularioJogo()
    form.nome.data = jogo.nome
    form.categoria.data = jogo.categoria
    form.console.data = jogo.console
    capa_jogo = recupera_imagem(id)
    return render_template('editar.html', titulo='Editar Jogo', id=id, capa_jogo=capa_jogo, form=form)
# FIM - Rota para formulario de editar

# Capturar informações inseridas na area html editar, para alterar o jogo cadastrado
@app.route('/atualizar', methods=['POST'])
def atualizar():

    form = FormularioJogo(request.form)

    if form.validate_on_submit():

        jogo = Jogos.query.filter_by(id=request.form['id']).first()

        jogo.nome = form.nome.data
        jogo.categoria = form.categoria.data
        jogo.console = form.console.data

        db.session.add(jogo)
        db.session.commit()

        upload_path = app.config['UPLOAD_PATH']
        arquivo = request.files['arquivo']
        timestamp = time.time()
        deleta_arquivo(jogo.id)
        arquivo.save(f'{upload_path}/capa{jogo.id}-{timestamp}.jpg')

    return redirect(url_for('index'))
# FIM - Capturar informações inseridas na area html editar, para alterar o jogo cadastrado


# ROTA PARA DELETAR UM JOGO
@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    Jogos.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Jogo deletado com sucesso')

    return redirect(url_for('index'))
# FIM - ROTA PARA DELETAR UM JOGO


@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)


