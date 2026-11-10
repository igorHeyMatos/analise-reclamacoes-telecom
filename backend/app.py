"""Back-end em Flask: recebe os pedidos do front-end e responde em JSON."""
from datetime import datetime

from flask import Flask, jsonify, request

import dados
import modelo

app = Flask(__name__)
app.json.sort_keys = False  # mantém a ordem dos dados (do maior para o menor) no JSON

# Estado da aplicação, guardado na memória enquanto o servidor estiver ligado
estado = {
    "base": None,          # DataFrame limpo da base atual
    "nome_base": None,     # nome do arquivo da base atual
    "resumo": None,        # números dos gráficos, calculados uma vez quando a base chega
    "modelo": None,        # classificador treinado
    "base_do_modelo": None,
    "historico": [],       # todos os treinos feitos
    "pendentes": None,     # reclamações ainda sem avaliação, que o modelo vai prever
    "previsoes": None,     # previsão de todas as pendentes, feita a cada treino
    "caracteristicas": None,  # chance média prevista por característica (o "porquê")
}


def erro(mensagem, status=400):
    return jsonify({"erro": mensagem}), status


@app.get("/status")
def status():
    return jsonify({
        "base": estado["nome_base"],
        "linhas": None if estado["base"] is None else len(estado["base"]),
        "base_do_modelo": estado["base_do_modelo"],
    })


@app.post("/dados")
def enviar_dados():
    arquivo = request.files.get("arquivo")
    if arquivo is None:
        return erro("Nenhum arquivo enviado.")

    try:
        df = dados.ler_arquivo(arquivo.read(), arquivo.filename)
    except ValueError as e:
        return erro(str(e))

    faltando = dados.colunas_faltando(df)
    if faltando:
        return erro("Colunas obrigatórias ausentes: " + ", ".join(faltando))

    base, etapas = dados.limpar(df)
    if len(base) < 50:
        return erro("Depois da limpeza sobraram menos de 50 reclamações. Envie uma base maior.")

    # Uma base nova substitui a anterior: o modelo precisa ser retreinado
    estado["base"] = base
    estado["nome_base"] = arquivo.filename
    estado["resumo"] = dados.resumir(base)
    estado["pendentes"] = dados.separar_pendentes(df)
    return jsonify({
        "arquivo": arquivo.filename,
        "etapas": [{"etapa": nome, "linhas": linhas} for nome, linhas in etapas],
        "pendentes": len(estado["pendentes"]),
        "previa": base.head(8).to_dict(orient="records"),
    }), 201


@app.get("/dados/resumo")
def resumo():
    if estado["base"] is None:
        return erro("Nenhuma base enviada ainda.", 404)
    return jsonify(estado["resumo"])


@app.post("/modelo/treinar")
def treinar():
    if estado["base"] is None:
        return erro("Envie uma base antes de treinar.", 404)

    pedido = request.get_json() or {}
    tipo = pedido.get("classificador")
    parametro = pedido.get("parametro")
    tamanho_teste = pedido.get("tamanho_teste", 0.2)
    if not isinstance(tamanho_teste, (int, float)) or not 0.1 <= tamanho_teste <= 0.4:
        return erro("A parte de teste deve ficar entre 10% e 40%.")

    try:
        modelo_treinado, metricas = modelo.treinar(estado["base"], tipo, parametro, tamanho_teste)
    except (ValueError, TypeError) as e:
        return erro(str(e))

    estado["modelo"] = modelo_treinado
    estado["base_do_modelo"] = estado["nome_base"]

    # Com o modelo novo, prevê de uma vez todas as reclamações ainda sem avaliação
    pendentes = estado["pendentes"]
    if pendentes is not None and len(pendentes) > 0:
        previsoes = modelo.prever_lote(modelo_treinado, pendentes)
        estado["caracteristicas"] = modelo.explicar(previsoes)
        previsoes["motivo"] = modelo.principal_motivo(previsoes, estado["caracteristicas"])
        estado["previsoes"] = previsoes
    else:
        estado["previsoes"] = None

    registro = {"base": estado["nome_base"], "classificador": tipo, "parametro": parametro,
                "treinado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), **metricas}
    estado["historico"].append(registro)
    return jsonify(registro)


@app.get("/modelo/historico")
def historico():
    return jsonify(estado["historico"])


@app.post("/modelo/prever")
def prever():
    if estado["modelo"] is None:
        return erro("Treine um modelo antes de prever.", 404)

    reclamacao = request.get_json() or {}
    faltando = [coluna for coluna in dados.COLUNAS_MODELO if coluna not in reclamacao]
    if faltando:
        return erro("Campos ausentes: " + ", ".join(faltando))

    return jsonify(modelo.prever(estado["modelo"], reclamacao))


@app.get("/previsoes")
def previsoes():
    if estado["modelo"] is None:
        return erro("Treine um modelo antes de ver as previsões.", 404)
    if estado["previsoes"] is None:
        return erro("A base usada no treino não tem reclamações sem avaliação para prever.", 404)

    return jsonify({
        "base": estado["base_do_modelo"],
        "previsoes": estado["previsoes"].to_dict(orient="records"),
        "caracteristicas": estado["caracteristicas"].to_dict(orient="records"),
    })


@app.post("/modelo/cenarios")
def cenarios():
    if estado["modelo"] is None:
        return erro("Treine um modelo antes de comparar cenários.", 404)

    pedido = request.get_json() or {}
    faltando = [campo for campo in ["Problema", "UF", "Procurou Empresa"] if campo not in pedido]
    if faltando:
        return erro("Campos ausentes: " + ", ".join(faltando))

    resultado = modelo.cenarios(estado["modelo"], estado["base"], pedido["Problema"], pedido["UF"],
                                pedido["Procurou Empresa"])
    return jsonify(resultado.to_dict(orient="records"))


if __name__ == "__main__":
    # use_reloader=False: sem reinício automático, que apagaria a base e o modelo da memória
    app.run(debug=True, use_reloader=False, port=5000)
