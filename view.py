from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
import jwt

senha_secreta = app.config['SECRET_KEY']

def generate_token(user_id):
    payload = {'id_usuario': user_id}
    token = jwt.encode(payload, senha_secreta, algorithm='HS255')
    return token

@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro")
    livros = cur.fetchall()
    livros_dic = []
    for livro in livros:
        livros_dic.append({
            'id_livro': livro [0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]

        })
    return jsonify(mensagem='lista de livros', livros=livros_dic)



@app.route('/livros', methods=['POST'])
def livros_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM LIVROS WHERE TITULO = ?", (titulo,))
    if cursor.fetchone():
        return jsonify('Livro já cadastrado')
    cursor.execute("INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?)",
                   (titulo, autor, ano_publicacao))

    con.commit()
    cursor.close()

    return jsonify({
     'message':'Livro cadastrado com sucesso!',
     'livro': {
         'titulo': titulo,
         'autor': autor,
         'ano_publicacao': ano_publicacao
        }
    })


@app.route('/livro_imagem', methods=['POST'])
def livro_imagem():
    token = request.headers.get('Authorization')
    if not token:
        return jsofiny({'mensagem:'Token de autenticação necessário}),

        token = remover_bearer(token)
        try:
            payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
            id_usuario = payload['id_usuario']
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401



        #Rota delete

@app.route('/livros/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    cursor = con.cursor()

    # Verificar se o livro existe
    cursor.execute("SELECT 1 FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    # Excluir o livro
    cursor.execute("DELETE FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro excluído com sucesso!",
        'id_livro': id
    })





#Rotas de usuário:


@app.route('/usuario', methods=['GET'])
def usuario():
    cur = con.cursor()
    cur.execute("SELECT id_usuario, nome, email, senha FROM usuario")
    usuario = cur.fetchall()
    usuario_dic = []
    for usuario in usuario:
        usuario_dic.append({
            'id_usuario': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'senha': usuario[3]
        })
    return jsonify(mensagem='Lista de usuarios', usuario=usuario_dic)

@app.route('/usuario', methods=['POST'])
def usuario_post():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM usuario WHERE nome = ?", (nome,))

    if cursor.fetchone():
        return jsonify("Usuario já cadastrado")

    senha = generate_password_hash(senha).decode('utf-8')

    cursor.execute("INSERT INTO usuario(nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({
        'menssage': 'Usuario cadastrado',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })

@app.route('/usuario/<int:id>', methods=['PUT'])
def usuario_put(id):
    cursor = con.cursor()
    cursor.execute(" select id_usuario, nome, email, senha from usuario where id_usuario = ?", (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({'Usuario não foi encontrado'})

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor.execute("update usuario set nome = ?, email = ?, senha = ? where id_usuario = ?", (nome, email, senha, id))

    con.commit()
    cursor.close()

    return jsonify({
        'menssage': 'Usuario cadastrado',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })

@app.route('/usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cursor = con.cursor()

    cursor.execute("SELECT senha, 1 FROM usuario WHERE ID_usuario = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuario não encontrado"})

    cursor.execute("DELETE FROM usuario WHERE ID_usuario = ?", (id,))
    con.commit()
    cursor.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT EMAIL FROM USUARIO WHERE EMAIL = ?', (email,))

    if not cursor.fetchone():
        return jsonify(mensagem='Email não encontrado.')

    cursor.execute('SELECT EMAIL, SENHA, id_usuario FROM USUARIO WHERE EMAIL = ?', (email,))

    usuario = cursor.fetchone()
    id_usuario = senha[1]

    if usuario and usuario[1] == senha:
        token = generate_token(id_usuario)
        return jsonify(mensagem='Login realizado com sucesso!')
    else:
        return jsonify(mensagem='Email ou senha incorretos.')


