# Global-Solution
repositorio para desenvolvimento do global solution. Criamos um suporte automatico para responder duvidas sobre carro eletrico

# Integrante (nome, RM)
Gabriel da silva amaral rm570421

Enzo Miguel de Oliveira Silva rm571639

# Documentação da Base de Conhecimento, Fontes Verificadas e Privacidade

## 1. Origem e Critérios de Confiabilidade das Fontes
O Citizen Assist AI foi construído exclusivamente sobre normas técnicas brasileiras, decretos estaduais/municipais e relatórios técnicos consolidados de entidades do setor:

1. **Associação Brasileira do Veículo Elétrico (ABVE) / SAE Brasil:**
   - Mapeamento da infraestrutura de recarga nacional, padrões de conectores adotados (Tipo 2 Mennekes e CCS2) e dados de confiabilidade.
2. **Agência Nacional de Energia Elétrica (ANEEL):**
   - Resolução Normativa nº 1.000/2021: Amparo regulatório para instalação de pontos de recarga em garagens coletivas e condomínios, estabelecendo as regras de medição e rateio sem revenda irregular de energia.
3. **Inmetro (Programa Brasileiro de Etiquetagem Veicular - PBEV):**
   - Dados de eficiência energética (km/kWh) e métricas comparativas de consumo com combustíveis fósseis.
4. **Legislações Tributárias e Governamentais (SEFAZ Estaduais / Prefeitura de SP):**
   - Diretrizes fiscais de IPVA por Unidade da Federação e Lei Municipal nº 15.997/2014 da capital paulista (dispensa do rodízio municipal).
5. **Legislação Ambiental e Segurança Técnica (ABNT / IBAMA):**
   - Lei Federal nº 12.305/2010 (logística reversa e reciclagem de baterias) e normas ABNT NBR 5410 / NBR 17019 para segurança de instalações elétricas de recarga.

## 2. Princípios de Privacidade e Tratamento de Dados (LGPD)
Em total conformidade com o edital do desafio CitizenTech:
- **Zero Coleta de Dados Pessoais:** O sistema opera sob o princípio da minimização. Em nenhum momento o usuário precisa fornecer CPF, nome, placa do veículo, e-mail ou localização precisa via GPS.
- **Transparência e Caráter Não-Oficial:** O assistente declara formalmente em seus avisos que atua como ferramenta informativa complementar, orientando o cidadão a verificar decretos e tarifas vigentes junto aos órgãos competentes.

## 3. Como Executar
Na raiz do projeto:

    python3 src/sistema.py          # inicia o assistente no terminal
    python3 src/teste_sistema.py    # roda os testes automáticos

Requisito: Python 3.8+ (usa apenas a biblioteca padrão).

## 4. Estrutura do Projeto
    data/base_conhecimento.json   # base com 18 registros em 3 temas
    src/gerenciador_dados.py      # Parte 1: carga, validação e persistência
    src/sistema.py                # Parte 2: índices, busca, menu e prompts
    src/teste_sistema.py          # testes automáticos

## 5. Funcionamento do Sistema
- **Estruturas de dados:** dicionários para busca por ID, por tema e por palavra-chave
  (índice invertido), além de uma árvore tema > subtema.
- **Busca:** o texto é normalizado (sem acentos e sem palavras comuns) e cada registro
  recebe uma pontuação (palavra-chave, subtema, pergunta e orientação). Com um vencedor
  claro, o sistema responde direto; com resultados parecidos, pede ao usuário que escolha
  entre as opções (desambiguação); sem resultado, exibe aviso.
- **Navegação continuada:** um grafo liga assuntos relacionados (inclusive entre temas) e
  sugere os próximos assuntos após cada resposta.
- **Modelos de resposta:**
  - **Modelo A (Direto/Técnico):** objetivo, com fonte, data de verificação e aviso curto.
  - **Modelo B (Didático/Cidadão):** linguagem simples, repete a dúvida do usuário e
    sempre exibe o aviso legal completo.
- **Alertas:** registros que dependem de legislação local exibem pedido de confirmação
  com o órgão competente. Entradas inválidas e assuntos fora da base também geram aviso.

## 6. Limitações
- A base cobre apenas os temas cadastrados; cada registro tem data de verificação e a
  informação pode ter mudado desde então.
- A aplicação é informativa e não substitui órgãos oficiais, fabricantes,
  concessionárias de energia ou profissionais habilitados.