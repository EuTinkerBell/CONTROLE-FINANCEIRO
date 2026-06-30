from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# O seu token exato da API Meu Danfe
API_KEY = "6c08eba5-abe8-4e4d-9d9f-06de840ae7ff"

# HTML da estrutura principal dividida (Dashboard)
HTML_PRINCIPAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Integrado de Consultas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body, html { width: 100%; height: 100%; font-family: Arial, sans-serif; overflow: hidden; background-color: #f0f2f5; }
        .container { display: flex; width: 100%; height: 100%; }
        .painel { flex: 1; height: 100%; border: none; }
        .painel:first-child { border-right: 3px solid #1a73e8; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Lado Esquerdo: Consulta CNPJ -->
        <iframe src="/cnpj" class="painel"></iframe>
        
        <!-- Lado Direito: Consulta Nota Fiscal -->
        <iframe src="/nf" class="painel"></iframe>
    </div>
</body>
</html>
"""

# HTML do projeto Nota Fiscal (criado para rodar no navegador)
HTML_NOTA_FISCAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta Nota Fiscal</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .card { width: 100%; max-width: 550px; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h2 { color: #e67e22; text-align: center; margin-top: 0; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; transition: 0.3s; }
        input:focus { border-color: #e67e22; }
        button.primary { padding: 12px 20px; background: #e67e22; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 100%; }
        button.primary:hover { background: #d35400; }
        #resultado { background: #fafafa; border-radius: 8px; padding: 15px; display: none; border: 1px solid #eee; font-size: 14px; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #d93025; font-weight: bold; }
        pre { background: #eee; padding: 10px; border-radius: 5px; font-size: 11px; overflow-x: auto; }
    </style>
</head>
<body>
<div class="card">
    <h2>Consultor de Nota Fiscal (Meu Danfe)</h2>
    <div class="input-group">
        <input type="text" id="chaveInput" placeholder="Digite a Chave da NF (44 números)" maxlength="44">
        <button class="primary" onclick="consultarNF()">Enviar para Fila</button>
    </div>
    <div id="resultado"></div>
</div>

<script>
    async function consultarNF() {
        const chave = document.getElementById('chaveInput').value.replace(/\D/g, '');
        const resDiv = document.getElementById('resultado');
        
        if(chave.length !== 44) {
            resDiv.style.display = 'block';
            resDiv.innerHTML = '<p class="error">A chave deve conter exatamente 44 números.</p>';
            return;
        }
        
        resDiv.style.display = 'block';
        resDiv.innerHTML = '<em>Enviando nota para a fila do Meu Danfe...</em>';
        
        try {
            const response = await fetch('/api/consultar-nf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chave: chave })
            });
            
            const dados = await response.json();
            
            if (response.status === 200) {
                resDiv.innerHTML = `
                    <p class="success">✅ Requisição aceita!</p>
                    <p><strong>Status da Nota:</strong> ${dados.status || '---'}</p>
                    <p><strong>Mensagem:</strong> ${dados.msg || ''}</p>
                    <br><strong>Resposta completa da API:</strong>
                    <pre>${JSON.stringify(dados.raw, null, 2)}</pre>
                `;
            } else {
                resDiv.innerHTML = `<p class="error">❌ Erro ${response.status}: ${dados.erro}</p>`;
            }
        } catch (err) {
            resDiv.innerHTML = `<p class="error">Erro técnico: ${err.message}</p>`;
        }
    }
</script>
</body>
</html>
"""

# Rota principal (Dashboard Lado a Lado)
@app.route('/')
def index():
    return render_template_string(HTML_PRINCIPAL)

# Rota que carrega o projeto CNPJ (HTML que você me enviou)
@app.route('/cnpj')
def cnpj_page():
    # Carrega diretamente o HTML que você me passou
    with open('cnpj.html', 'r', encoding='utf-8') as f:
        return f.read()

# Rota que carrega a interface gráfica da Nota Fiscal
@app.route('/nf')
def nf_page():
    return render_template_string(HTML_NOTA_FISCAL)

# Rota interna (API) que executa o seu script Python antigo da NF
@app.route('/api/consultar-nf', methods=['POST'])
def api_consultar_nf():
    data = request.json
    chave_nota = data.get('chave')
    
    url = f"https://api.meudanfe.com.br/v2/fd/add/{chave_nota}"
    headers = {
        "Api-Key": API_KEY, 
        "Accept": "application/json"
    }
    
    try:
        response = requests.put(url, headers=headers)
        
        if response.status_code == 200:
            dados = response.json()
            status_api = dados.get("status", "")
            msg = ""
            if status_api in ["WAITING", "SEARCHING"]:
                msg = "⏳ A nota entrou na fila. Aguarde uns segundos e consulte de novo para obter o OK."
            
            return jsonify({"status": status_api, "msg": msg, "raw": dados}), 200
        elif response.status_code == 400:
            return jsonify({"erro": "A chave informada é inválida (verifique os 44 números)."}), 400
        elif response.status_code == 401:
            return jsonify({"erro": "O seu Api-Key está incorreto ou revogado."}), 401
        else:
            return jsonify({"erro": response.text}), response.status_code
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=False)