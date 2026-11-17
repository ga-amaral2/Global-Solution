import os
from gerenciador_dados import GerenciadorBaseConhecimento  # mesmo nome usado no sistema.py
from system import IndiceConhecimento

caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "base_conhecimento.json")
indice = IndiceConhecimento(GerenciadorBaseConhecimento(caminho).carregar_e_validar())

def primeiro_id(consulta):
    return indice.buscar(consulta)[0][1]["id"]

# estrutura
assert len(indice.temas()) == 3, "deveria haver 3 temas"
assert len(indice.por_id) == 18, "deveria haver 18 registros"

# busca com resultado claro
assert primeiro_id("ipva") == 14
assert primeiro_id("wallbox") == 8
assert primeiro_id("tomada comum") == 7
assert primeiro_id("rodízio em São Paulo") == 15

# busca ambígua e busca sem resultado
assert len(indice.buscar("bateria")) > 1
assert indice.buscar("salada de frutas") == []

# grafo: cada registro tem 3 vizinhos e nenhum é ele mesmo
for rid, vizinhos in indice.grafo.items():
    assert len(vizinhos) == 3 and rid not in vizinhos, f"grafo com problema no ID {rid}"

print("Todos os testes passaram!")