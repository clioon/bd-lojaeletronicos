from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "dbname": "kabom",
    "user": "postgres",
    "password": "abc123",
    "host": "localhost",
    "port": "5432"
}

def conectar():
    """Cria e retorna uma conexão com o banco PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

@app.route("/")
def home():
    try:
        conn = conectar()
        conn.close()
        return "Conexão com PostgreSQL funcionando! 🎉"
    except Exception as e:
        return f"Erro ao conectar: {e}"

@app.route("/criar_cliente", methods=["POST"])
def criar_cliente():
    dados = request.json

    nome = dados.get("nome")
    cidade = dados.get("cidade")
    estado = dados.get("estado")
    pais = dados.get("pais")

    if not all([nome, cidade, estado, pais]):
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Cliente (nome_cliente, cidade, estado, pais)
            VALUES (%s, %s, %s, %s)
            RETURNING id_cliente;
        """, (nome, cidade, estado, pais))

        id_gerado = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Cliente criado com sucesso!", "id": id_gerado})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
