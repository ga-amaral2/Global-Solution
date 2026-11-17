import os
import re
import sys
import textwrap
import unicodedata

from gerenciador_dados import GerenciadorBaseConhecimento


# ======================================================================
# 0. UTILITÁRIOS DE TEXTO
# ======================================================================
# Palavras sem valor de busca. "carro", "elétrico" etc. entram aqui porque
# aparecem em quase todas as perguntas e não ajudam a distinguir registros.
STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na",
    "nos", "nas", "um", "uma", "e", "ou", "que", "para", "por", "com", "se",
    "meu", "minha", "posso", "pode", "como", "qual", "quais", "quanto",
    "quando", "ao", "pelo", "pela", "ser", "tem", "ter", "eu", "me", "mais",
    "sobre", "tudo", "carro", "carros", "eletrico", "eletricos", "veiculo",
    "veiculos", "ve", "ves", "existe", "quero", "saber", "preciso",
}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação. Ex.: 'Bateria?' -> 'bateria'."""
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def tokenizar(texto):
    """Normaliza e devolve a lista de palavras úteis (sem stopwords)."""
    return [t for t in normalizar(texto).split() if t not in STOPWORDS and len(t) >= 2]


def formatar_data(iso):
    """'2026-03-10' -> '10/03/2026' (se não for ISO, devolve como veio)."""
    partes = str(iso).split("-")
    return "/".join(reversed(partes)) if len(partes) == 3 else str(iso)


def quebrar(texto, largura=78, recuo="  "):
    return textwrap.fill(texto, width=largura, initial_indent=recuo, subsequent_indent=recuo)


# ======================================================================
# 1. ESTRUTURA DE DADOS: ÍNDICES, ÁRVORE E GRAFO
# ======================================================================
# Ligações escolhidas à mão entre assuntos que fazem sentido ler em sequência
# (inclusive entre temas diferentes). O grafo completa o resto automaticamente.
LIGACOES_MANUAIS = {
    1: [2, 17], 2: [1, 6], 3: [5, 2], 4: [13, 17], 5: [3, 8], 6: [2, 17],
    7: [8, 9], 8: [7, 9], 9: [8, 14], 10: [11, 12], 11: [10, 12], 12: [11, 10],
    13: [18, 4], 14: [15, 13], 15: [14, 13], 16: [17, 18], 17: [1, 16],
    18: [13, 16],
}


class IndiceConhecimento:
    """Organiza os registros em estruturas que tornam a busca rápida.

    Atributos principais
    --------------------
    por_id      : {id: registro}
    por_tema    : {tema: [ids]}
    arvore      : {tema: {subtema: id}}           (raiz > tema > subtema)
    invertido   : {palavra: {ids}}                (palavra-chave -> registros)
    grafo       : {id: [ids relacionados]}        (navegação continuada)
    """

    def __init__(self, registros):
        self.por_id = {}
        self.por_tema = {}
        self.arvore = {}
        self.invertido = {}
        self.grafo = {}
        self._campos = {}  # tokens pré-calculados por registro (usado na busca)

        for reg in registros:
            self._indexar(reg)
        self._construir_grafo()

    # ---------------- construção ----------------
    def _indexar(self, reg):
        rid = reg["id"]
        self.por_id[rid] = reg
        self.por_tema.setdefault(reg["tema"], []).append(rid)
        self.arvore.setdefault(reg["tema"], {})[reg["subtema"]] = rid

        frases = [normalizar(k) for k in reg["palavras_chave"]]
        kw_tokens = {t for f in frases for t in f.split() if t not in STOPWORDS}
        self._campos[rid] = {
            "frases": frases,
            "kw": kw_tokens,
            "sub": set(tokenizar(reg["subtema"])),
            "perg": set(tokenizar(reg["pergunta_referencia"])),
            "orient": set(tokenizar(reg["orientacao_resumida"])),
        }
        for t in kw_tokens:
            self.invertido.setdefault(t, set()).add(rid)

    def _construir_grafo(self):
        """Cada nó recebe até 3 vizinhos: primeiro as ligações manuais, depois os
        mais parecidos (palavras em comum + mesmo tema)."""
        for rid in self.por_id:
            vizinhos = [v for v in LIGACOES_MANUAIS.get(rid, []) if v in self.por_id and v != rid]
            candidatos = sorted(
                (o for o in self.por_id if o != rid and o not in vizinhos),
                key=lambda o: self._afinidade(rid, o),
                reverse=True,
            )
            for o in candidatos:
                if len(vizinhos) >= 3:
                    break
                vizinhos.append(o)
            self.grafo[rid] = vizinhos[:3]

    def _afinidade(self, a, b):
        ca, cb = self._campos[a], self._campos[b]
        mesmo_tema = 1 if self.por_id[a]["tema"] == self.por_id[b]["tema"] else 0
        return 2 * len(ca["kw"] & cb["kw"]) + 0.5 * len(ca["perg"] & cb["perg"]) + mesmo_tema

    # ---------------- consultas simples ----------------
    def temas(self):
        return sorted(self.por_tema)

    def subtemas(self, tema):
        """Lista [(id, subtema)] de um tema, na ordem dos IDs."""
        return sorted(((i, s) for s, i in self.arvore.get(tema, {}).items()))

    def relacionados(self, rid):
        return [self.por_id[i] for i in self.grafo.get(rid, [])]

    # ---------------- busca por texto ----------------
    def buscar(self, consulta):
        """Devolve [(pontuacao, registro)] ordenado do mais para o menos relevante.

        Pesos:  palavra-chave exata +3 | mesmo radical (5 letras) +2 |
                frase-chave inteira (ex.: 'tomada comum') +2 extra |
                palavra no subtema +2 | na pergunta +1 | na orientação +0,5
        Só entram registros com pontuação >= LIMIAR_MINIMO.
        """
        tokens = tokenizar(consulta)
        consulta_norm = " " + normalizar(consulta) + " "
        resultados = []

        for rid, c in self._campos.items():
            pontos = 0.0
            for t in tokens:
                if t in c["kw"]:
                    pontos += 3
                elif self._mesmo_radical(t, c["kw"]):
                    pontos += 2
                if t in c["sub"]:
                    pontos += 2
                if t in c["perg"]:
                    pontos += 1
                if t in c["orient"]:
                    pontos += 0.5
            for frase in c["frases"]:
                if " " in frase and f" {frase} " in consulta_norm:
                    pontos += 2
            if pontos >= LIMIAR_MINIMO:
                resultados.append((pontos, self.por_id[rid]))

        resultados.sort(key=lambda x: (-x[0], x[1]["id"]))
        return resultados

    @staticmethod
    def _mesmo_radical(token, conjunto):
        if len(token) < 5:
            return False
        return any(len(k) >= 5 and k[:5] == token[:5] for k in conjunto)


LIMIAR_MINIMO = 2.0        # abaixo disso, considera "não encontrado"
RAZAO_DESTAQUE = 1.5       # 1º lugar precisa ter 1,5x a nota do 2º para ser resposta direta
MAX_OPCOES = 4             # máximo de opções mostradas na desambiguação


# ======================================================================
# 2. MODELOS DE PROMPT / INSTRUÇÃO DE RESPOSTA
# ======================================================================
AVISO_LEGAL = (
    "AVISO: esta aplicação tem caráter informativo e NÃO substitui órgãos oficiais, "
    "fabricantes, concessionárias de energia, prefeituras ou profissionais habilitados. "
    "Confirme sempre nas fontes oficiais antes de tomar decisões."
)

AVISO_CONFIRMACAO = (
    "ATENÇÃO: este assunto depende de legislação/normas que mudam por estado, município "
    "ou condomínio. Confirme com o órgão competente (SEFAZ, prefeitura, ANEEL, "
    "distribuidora ou convenção do condomínio)."
)

AVISO_NAO_ENCONTRADO = (
    "Não encontrei esse assunto na base de conhecimento. Tente outras palavras "
    "(ex.: 'bateria', 'wallbox', 'IPVA') ou use a navegação por temas.\n"
    "Lembrete: a base cobre apenas os temas cadastrados e não substitui órgãos oficiais."
)

AVISO_INVALIDO = (
    "Entrada inválida: digite ao menos uma palavra com 3 letras ou mais "
    "(sem apenas números ou símbolos)."
)


def modelo_a_tecnico(reg):
    """MODELO A - Direto/Técnico.
    Instrução: responder em tom objetivo, sem rodeios, citando tema, a orientação
    e a fonte com data de verificação. Aviso legal reduzido a uma linha."""
    linhas = [
        f"[MODELO A - TÉCNICO]  {reg['tema']} > {reg['subtema']}",
        quebrar(reg["orientacao_resumida"]),
        f"  Fonte: {reg['referencia_consultada']} (verificado em {formatar_data(reg['data_verificacao'])})",
    ]
    if reg.get("exige_confirmacao_adicional"):
        linhas.append(quebrar(AVISO_CONFIRMACAO))
    linhas.append("  * Informativo; não substitui órgãos oficiais.")
    return "\n".join(linhas)


def modelo_b_didatico(reg):
    """MODELO B - Didático/Cidadão com aviso legal.
    Instrução: responder em linguagem simples, repetir a dúvida do usuário,
    explicar a orientação, indicar onde confirmar e SEMPRE exibir o aviso legal
    completo."""
    linhas = [
        f"[MODELO B - DIDÁTICO]  {reg['tema']} > {reg['subtema']}",
        quebrar(f"Sua dúvida: \"{reg['pergunta_referencia']}\""),
        "",
        quebrar("Em linguagem simples: " + reg["orientacao_resumida"]),
        "",
        quebrar(
            f"Onde conferir: {reg['referencia_consultada']} "
            f"(informação verificada em {formatar_data(reg['data_verificacao'])})."
        ),
    ]
    if reg.get("exige_confirmacao_adicional"):
        linhas += ["", quebrar(AVISO_CONFIRMACAO)]
    linhas += ["", quebrar(AVISO_LEGAL)]
    return "\n".join(linhas)


MODELOS = {
    "A": ("Direto / Técnico", modelo_a_tecnico),
    "B": ("Didático / Cidadão com aviso legal", modelo_b_didatico),
}


# ======================================================================
# 3. MENU INTERATIVO NO TERMINAL
# ======================================================================
LINHA = "=" * 64


class MenuTerminal:
    def __init__(self, indice, modelo="B"):
        self.indice = indice
        self.modelo = modelo

    # ---------- entrada/saída ----------
    @staticmethod
    def _ler(msg):
        try:
            return input(msg).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            sys.exit(0)

    def _mostrar_resposta(self, reg):
        print("\n" + LINHA)
        print(MODELOS[self.modelo][1](reg))
        print(LINHA)
        self._navegar_relacionados(reg["id"])

    # ---------- navegação continuada (grafo) ----------
    def _navegar_relacionados(self, rid):
        """Após cada resposta, sugere assuntos ligados no grafo. Pode encadear."""
        while True:
            rel = self.indice.relacionados(rid)
            if not rel:
                return
            print("\nAssuntos relacionados:")
            for n, r in enumerate(rel, 1):
                print(f"  {n}. {r['subtema']}  ({r['tema']})")
            op = self._ler("Digite o número para continuar ou ENTER para voltar ao menu: ")
            if not op:
                return
            if op.isdigit() and 1 <= int(op) <= len(rel):
                rid = rel[int(op) - 1]["id"]
                print("\n" + LINHA)
                print(MODELOS[self.modelo][1](self.indice.por_id[rid]))
                print(LINHA)
            else:
                print("Opção inválida.")

    # ---------- opção 1: busca por texto ----------
    def buscar_por_texto(self):
        consulta = self._ler("\nDigite sua dúvida (ou palavras-chave): ")
        if len(re.sub(r"[^A-Za-zÀ-ÿ]", "", consulta)) < 3:
            print("\n" + AVISO_INVALIDO)
            return

        resultados = self.indice.buscar(consulta)
        if not resultados:
            print("\n" + AVISO_NAO_ENCONTRADO)
            return

        # --- lógica de desambiguação ---
        melhor = resultados[0][0]
        segundo = resultados[1][0] if len(resultados) > 1 else 0
        if len(resultados) == 1 or melhor >= RAZAO_DESTAQUE * segundo:
            self._mostrar_resposta(resultados[0][1])  # correspondência clara
            return

        print("\nEncontrei mais de um assunto possível. Qual deles você quer?")
        opcoes = [r for _, r in resultados[:MAX_OPCOES]]
        for n, r in enumerate(opcoes, 1):
            print(f"  {n}. {r['subtema']}  ({r['tema']})")
            print(f"     \"{r['pergunta_referencia']}\"")
        print("  0. Nenhum deles (refazer a busca)")
        while True:
            op = self._ler("Escolha: ")
            if op == "0":
                return
            if op.isdigit() and 1 <= int(op) <= len(opcoes):
                self._mostrar_resposta(opcoes[int(op) - 1])
                return
            print("Opção inválida. Digite um dos números listados.")

    # ---------- opção 2: navegação por temas ----------
    def navegar_por_temas(self):
        temas = self.indice.temas()
        while True:
            print("\nTEMAS DISPONÍVEIS")
            for n, t in enumerate(temas, 1):
                print(f"  {n}. {t}")
            print("  0. Voltar")
            op = self._ler("Escolha o tema: ")
            if op == "0":
                return
            if not (op.isdigit() and 1 <= int(op) <= len(temas)):
                print("Opção inválida.")
                continue
            self._menu_subtemas(temas[int(op) - 1])

    def _menu_subtemas(self, tema):
        subs = self.indice.subtemas(tema)
        while True:
            print(f"\n{tema.upper()}")
            for n, (_, s) in enumerate(subs, 1):
                print(f"  {n}. {s}")
            print("  0. Voltar aos temas")
            op = self._ler("Escolha o assunto: ")
            if op == "0":
                return
            if op.isdigit() and 1 <= int(op) <= len(subs):
                self._mostrar_resposta(self.indice.por_id[subs[int(op) - 1][0]])
            else:
                print("Opção inválida.")

    # ---------- opção 3: modelo de resposta ----------
    def trocar_modelo(self):
        print("\nMODELOS DE RESPOSTA")
        for k, (nome, _) in MODELOS.items():
            marca = "  <- atual" if k == self.modelo else ""
            print(f"  {k}. {nome}{marca}")
        op = self._ler("Escolha (A/B): ").upper()
        if op in MODELOS:
            self.modelo = op
            print(f"Modelo {op} ativado.")
        else:
            print("Opção inválida; modelo mantido.")

    # ---------- opção 4: limitações ----------
    @staticmethod
    def mostrar_sobre():
        print("\nSOBRE E LIMITAÇÕES")
        print(quebrar(AVISO_LEGAL))
        print(quebrar("A base é limitada aos temas cadastrados e cada registro tem data de "
                      "verificação; informações podem ter mudado desde então."))

    # ---------- laço principal ----------
    def executar(self):
        print(LINHA)
        print(" ASSISTENTE DE MOBILIDADE ELÉTRICA ".center(64, "="))
        print(LINHA)
        print(quebrar(AVISO_LEGAL, recuo=""))
        acoes = {
            "1": self.buscar_por_texto,
            "2": self.navegar_por_temas,
            "3": self.trocar_modelo,
            "4": self.mostrar_sobre,
        }
        while True:
            print("\nMENU PRINCIPAL")
            print("  1. Buscar por pergunta / palavra-chave")
            print("  2. Navegar por temas")
            print(f"  3. Trocar modelo de resposta (atual: {self.modelo})")
            print("  4. Sobre e limitações")
            print("  0. Sair")
            op = self._ler("Escolha: ")
            if op == "0":
                print("Até logo!")
                return
            acao = acoes.get(op)
            if acao:
                acao()
            else:
                print("Opção inválida. Digite um número do menu.")


# ======================================================================
# 4. PONTO DE ENTRADA
# ======================================================================
def main():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio, "..", "data", "base_conhecimento.json")

    gerenciador = GerenciadorBaseConhecimento(caminho)
    try:
        registros = gerenciador.carregar_e_validar()
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Não foi possível iniciar o sistema.\n{e}")
        sys.exit(1)

    MenuTerminal(IndiceConhecimento(registros)).executar()


if __name__ == "__main__":
    main()