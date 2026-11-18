import os
import re
import time
from gerenciador_dados import GerenciadorBaseConhecimento
from system import IndiceConhecimento, RAZAO_DESTAQUE

# 12 perguntas: diretas, variações de frase e fora dos 3 temas
CASOS_DE_TESTE = [
    # --- Dúvidas diretas (6) ---
    {"id": "T01", "tipo": "Direta", "pergunta": "Qual a garantia da bateria?", "esperado": 1},
    {"id": "T02", "tipo": "Direta", "pergunta": "Como funciona o carregamento rápido na rodovia?", "esperado": 11},
    {"id": "T03", "tipo": "Direta", "pergunta": "Carro elétrico paga IPVA?", "esperado": 14},
    {"id": "T04", "tipo": "Direta", "pergunta": "Quais conectores existem no Brasil?", "esperado": 10},
    {"id": "T05", "tipo": "Direta", "pergunta": "O síndico pode proibir wallbox no condomínio?", "esperado": 9},
    {"id": "T06", "tipo": "Direta", "pergunta": "Carro elétrico pega fogo fácil?", "esperado": 3},

    # --- Variações de frases / reformulações (4) ---
    {"id": "T07", "tipo": "Variação", "pergunta": "Preciso trocar óleo e correia dentada?", "esperado": 4},
    {"id": "T08", "tipo": "Variação", "pergunta": "Posso passar em rua alagada sem tomar choque?", "esperado": 5},
    {"id": "T09", "tipo": "Variação", "pergunta": "Em quanto tempo o investimento se paga rodando muito?", "esperado": 18},
    {"id": "T10", "tipo": "Variação", "pergunta": "Onde encontro mapa de eletropostos na cidade?", "esperado": 12},

    # --- Fora dos 3 temas (2) -> esperado: None (não encontrado) ---
    {"id": "T11", "tipo": "Fora do escopo", "pergunta": "Como tirar segunda via do RG?", "esperado": None},
    {"id": "T12", "tipo": "Fora do escopo", "pergunta": "Qual o valor da multa por excesso de velocidade?", "esperado": None},
]

def classificar_saida(indice, texto):
    # Replica a mesma lógica de decisão do MenuTerminal:
    if len(re.sub(r"[^A-Za-zÀ-ÿ]", "", texto)) < 3:
        return "ENTRADA_INVALIDA", None

    resultados = indice.buscar(texto)
    if not resultados:
        return "NAO_ENCONTRADO", None

    melhor = resultados[0][0]
    segundo = resultados[1][0] if len(resultados) > 1 else 0
    if len(resultados) == 1 or melhor >= RAZAO_DESTAQUE * segundo:
        return "RESPOSTA_DIRETA", resultados[0][1]["id"]

    ids_ambiguos = [r["id"] for _, r in resultados[:4]]
    return "AMBIGUO", ids_ambiguos


def executar_bateria():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio, "..", "data", "base_conhecimento.json")

    registros = GerenciadorBaseConhecimento(caminho).carregar_e_validar()
    indice = IndiceConhecimento(registros)

    acertos = 0
    tempos_ms = []

    print("=" * 78)
    print(" BATERIA DE TESTES AUTOMATIZADOS (12 CONSULTAS) ".center(78, "="))
    print("=" * 78)

    for caso in CASOS_DE_TESTE:
        inicio = time.perf_counter()
        status, obtido = classificar_saida(indice, caso["pergunta"])
        fim = time.perf_counter()

        duracao_ms = (fim - inicio) * 1000
        tempos_ms.append(duracao_ms)

        # Verifica acerto:
        # - Se esperado é um ID: acertou se respondeu direto com o ID ou se ofereceu ele na desambiguação
        # - Se esperado é None: acertou se identificou NAO_ENCONTRADO
        if caso["esperado"] is None:
            passou = status == "NAO_ENCONTRADO"
        elif status == "RESPOSTA_DIRETA":
            passou = obtido == caso["esperado"]
        elif status == "AMBIGUO":
            passou = caso["esperado"] in obtido
        else:
            passou = False

        if passou:
            acertos += 1

        marca = "ACERTO" if passou else "ERRO"
        print(
            f"[{caso['id']}] {marca:<6} | {caso['tipo']:<14} | "
            f"Esperado: {str(caso['esperado']):<4} | Obtido: {status} ({obtido}) | "
            f"{duracao_ms:.3f} ms"
        )

    total = len(CASOS_DE_TESTE)
    taxa_acerto = (acertos / total) * 100
    tempo_medio = sum(tempos_ms) / total

    print("-" * 78)
    print(f"Total de perguntas testadas : {total}")
    print(f"Respostas corretas          : {acertos}")
    print(f"Taxa de Acerto              : {taxa_acerto:.1f}%")
    print(f"Tempo Médio de Consulta     : {tempo_medio:.3f} ms")
    print("=" * 78)

    # 3 Cenários de Limitação
    print("\nTESTE DOS 3 CENÁRIOS DE LIMITAÇÃO")
    limitacoes = [
        ("L01 - Entrada vazia", "   "),
        ("L02 - Pergunta ambígua", "bateria"),
        ("L03 - Tema inexistente", "financiamento imobiliário caixa"),
    ]
    for nome, entrada in limitacoes:
        status, detalhe = classificar_saida(indice, entrada)
        print(f"  * {nome:<24} -> Entrada: '{entrada}' | Comportamento: {status} ({detalhe})")


if __name__ == "__main__":
    executar_bateria()