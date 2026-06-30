import subprocess
import time
import webbrowser
from flask import Flask, render_template_string

app = Flask(__name__)

PORTA_DASHBOARD = 3000
PORTA_CNPJ = 5000
PORTA_NOTAS = 8080

HTML_DASHBOARD = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Integrado Executivo</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; font-family: 'Segoe UI', sans-serif; overflow: hidden; background-color: #f1f5f9; }}
        .container {{ display: flex; width: 100%; height: 100%; }}
        .painel {{ flex: 1; height: 100%; border: none; }}
        .painel:first-child {{ border-right: 4px solid #2563eb; }} /* Divisor azul em destaque */
    </style>
</head>
<body>
    <div class="container">
        <!-- LADO ESQUERDO: Consulta CNPJ (Porta 5000) -->
        <iframe src="http://localhost:{PORTA_CNPJ}" class="painel" title="Consulta CNPJ"></iframe>
        
        <!-- LADO DIREITO: Fast Loader & Conciliador Exact (Porta 8080) -->
        <iframe src="http://localhost:{PORTA_NOTAS}" class="painel" title="Conciliador Exact"></iframe>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

def iniciar_tudo():
    print("🚀 Ligando os motores locais de consulta...")

    # Força a inicialização dos subprocessos garantindo as portas isoladas
    processo_cnpj = subprocess.Popen(["python", "app.py"])
    processo_notas = subprocess.Popen(["python", "painel.py"])
    
    # Dá um tempo de segurança para os servidores Flask estabilizarem nas portas 5000 e 8080
    time.sleep(3)
    
    # Abre uma ÚNICA aba no navegador principal para o Dashboard centralizador
    webbrowser.open(f"http://localhost:{PORTA_DASHBOARD}/")
    
    try:
        app.run(port=PORTA_DASHBOARD, debug=False, use_reloader=False)
    finally:
        print("\n🛑 Encerrando todos os painéis abertos...")
        processo_cnpj.terminate()
        processo_notas.terminate()

if __name__ == '__main__':
    iniciar_tudo()