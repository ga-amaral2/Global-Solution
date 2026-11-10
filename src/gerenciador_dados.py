import json
import os

CAMPOS_OBRIGATORIOS = [
    "id",
    "tema",
    "subtema",
    "palavras_chave",
    "pergunta_referencia",
    "orientacao_resumida",
    "referencia_consultada",
    "data_verificacao",
]


class GerenciadorBaseConhecimento:
    """Gerencia a persistência, validação e manutenção da base de conhecimento."""

    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.dados = []

    def carregar_e_validar(self):
        """Carrega a base JSON tratando arquivos ausentes, vazios ou registros inconsistentes."""
        if not os.path.exists(self.caminho_arquivo):
            raise FileNotFoundError(
                f"[ERRO DE DADOS] O arquivo '{self.caminho_arquivo}' não foi encontrado."
            )

        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(
                f"[ERRO DE DADOS] Arquivo corrompido ou JSON inválido: {err}"
            )

        if not isinstance(conteudo, list) or len(conteudo) == 0:
            raise ValueError(
                "[ERRO DE DADOS] O arquivo da base não pode estar vazio e precisa conter uma lista de registros."
            )

        # Validação de integridade registro por registro
        ids_vistos = set()
        for idx, registro in enumerate(conteudo, 1):
            if not isinstance(registro, dict):
                raise ValueError(
                    f"[ERRO DE DADOS] O registro na linha {idx} não é um objeto JSON válido."
                )

            for campo in CAMPOS_OBRIGATORIOS:
                if campo not in registro or registro[campo] is None:
                    raise KeyError(
                        f"[ERRO DE VALIDAÇÃO] Registro ID {registro.get('id', idx)} não possui o campo essencial '{campo}'."
                    )

            if registro["id"] in ids_vistos:
                raise ValueError(
                    f"[ERRO DE UNICIDADE] ID {registro['id']} duplicado detectado na base de dados."
                )
            ids_vistos.add(registro["id"])

        self.dados = conteudo
        return self.dados

    def listar_temas_disponiveis(self):
        """Retorna uma lista ordenada com os temas únicos existentes na base."""
        return sorted(list(set(item["tema"] for item in self.dados)))

    def adicionar_registro(self, novo_registro):
        """Permite inserir novos registros sem reescrever o código do sistema."""
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in novo_registro:
                raise KeyError(
                    f"Não é possível inserir o registro: campo obrigatório '{campo}' ausente."
                )

        # Autocalcular próximo ID caso não venha informado ou venha repetido
        ids_existentes = [r["id"] for r in self.dados]
        if "id" not in novo_registro or novo_registro["id"] in ids_existentes:
            novo_id = max(ids_existentes, default=0) + 1
            novo_registro["id"] = novo_id

        self.dados.append(novo_registro)
        self._salvar_arquivo()
        return novo_registro["id"]

    def atualizar_registro(self, id_registro, novos_dados):
        """Permite corrigir ou atualizar campos de um registro existente."""
        for idx, reg in enumerate(self.dados):
            if reg["id"] == id_registro:
                self.dados[idx].update(novos_dados)
                self._salvar_arquivo()
                return True
        return False

    def _salvar_arquivo(self):
        """Persiste as alterações em disco formatado de maneira legível."""
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)


# Bloco de auto-teste unitário da Parte 1
if __name__ == "__main__":
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(
        diretorio_atual, "..", "data", "base_conhecimento.json"
    )

    print("--- TESTE UNITÁRIO: PARTE 1 (GERENCIADOR DE DADOS) ---")
    gerenciador = GerenciadorBaseConhecimento(caminho_json)

    try:
        dados_carregados = gerenciador.carregar_e_validar()
        print(
            f"[✓] Base carregada e validada com sucesso: {len(dados_carregados)} registros."
        )

        temas = gerenciador.listar_temas_disponiveis()
        print(f"[✓] Temas catalogados ({len(temas)}): {', '.join(temas)}")

    except Exception as e:
        print(f"[X] Falha no teste da base: {e}")