# Global Solution - Citizen Tech
Assistente digital desenvolvido para a Global Solution 2026.2, com o objetivo de facilitar o acesso do cidadão a informações confiáveis e verificadas sobre carros elétricos, recarga e tributação.

## Integrantes
- Gabriel da Silva Amaral rm570421
- Enzo Miguel de Oliveira Silva rm571639
- Pedro Aulicino Corrêa Coelho rm570804

---

## 1. Descrição do Problema, Público-Alvo e Temas Abordados
Donos ou pessoas interessadas em veículos elétricos frequentemente encontram informações dispersas, termos técnicos complexos ou regras que variam por estado e município. O assistente organiza **18 orientações verificadas** divididas em **3 temas principais**:

1. **Manutenção e Bateria:** garantia padrão, degradação e boas práticas (20%–80%), segurança térmica, itens de revisão periódica, comportamento em alagamentos e reciclagem/logística reversa.
2. **Infraestrutura e Recarga:** recarga em tomada doméstica, Wallbox residencial, normas da ANEEL em condomínios, padrões de conectores no Brasil (Tipo 2 e CCS2), carregamento rápido em rodovias e aplicativos de localização.
3. **Custo-Benefício e Tributação:** custo por quilômetro rodado, regras estaduais de IPVA, dispensa do rodízio municipal em São Paulo, depreciação/valor residual, substituição modular de bateria e ponto de equilíbrio (*payback*).

---

## 2. Origem e Critérios de Confiabilidade das Fontes
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

---

## 3. Princípios de Privacidade e Tratamento de Dados (LGPD)
Em total conformidade com o edital do desafio CitizenTech:
- **Zero Coleta de Dados Pessoais:** O sistema opera sob o princípio da minimização. Em nenhum momento o usuário precisa fornecer CPF, nome, placa do veículo, e-mail ou localização precisa via GPS.
- **Transparência e Caráter Não-Oficial:** O assistente declara formalmente em seus avisos que atua como ferramenta informativa complementar, orientando o cidadão a verificar decretos e tarifas vigentes junto aos órgãos competentes.

---

## 4. Estrutura do Projeto
```text
├── data/
│   └── base_conhecimento.json   # Base estruturada com 18 registros em 3 temas
├── docs/
│   ├── plano_testes.md          # Metodologia, resultados das 12 consultas, User Test e melhorias
│   └── uso_ia.md                # Registro do uso de IA
├── src/
│   ├── gerenciador_dados.py     # Carga, validação e persistência da base JSON
│   ├── sistema.py               # Índices, busca, grafo, prompts e menu no terminal
│   ├── teste_sistema.py         # Testes unitários de integridade estrutural e grafo
│   └── avaliacao.py             # Bateria das 12 perguntas e cálculo de indicadores
└── README.md                    # Documentação geral do projeto
```

---

## 5. Como Executar
Na raiz do projeto:

```bash
python src/sistema.py          # inicia o assistente interativo no terminal
python src/avaliacao.py        # executa as 12 consultas de teste e calcula os indicadores
python src/teste_sistema.py    # roda os testes unitários de integridade da estrutura
```

Requisito: **Python 3.8+** (usa apenas a biblioteca padrão).

---


## 6. Funcionamento do Sistema
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

---

## 7. Exemplos de Funcionamento

### Exemplo 1 — Consulta válida com confirmação adicional (Modelo B)
**Entrada:** `Carro elétrico paga IPVA?`

```text
================================================================
[MODELO B - DIDÁTICO]  Custo-Benefício e Tributação > Isenção e Redução de IPVA
  Sua dúvida: "Carro elétrico tem isenção total de IPVA em todo o Brasil?"

  Em linguagem simples: A regra é estadual: DF, PR e RS oferecem isenção
  integral; RJ possui alíquota reduzida de 0,5%; SP adota políticas de
  restituição da cota municipal ou incentivos graduais definidos pela SEFAZ
  estadual.

  Onde conferir: Legislação Tributária Estadual - SEFAZ dos Estados
  (informação verificada em 01/03/2026).

  ATENÇÃO: este assunto depende de legislação/normas que mudam por estado,
  município ou condomínio. Confirme com o órgão competente (SEFAZ, prefeitura,
  ANEEL, distribuidora ou convenção do condomínio).

  AVISO: esta aplicação tem caráter informativo e NÃO substitui órgãos
  oficiais, fabricantes, concessionárias de energia, prefeituras ou
  profissionais habilitados. Confirme sempre nas fontes oficiais antes de
  tomar decisões.
================================================================
```

### Exemplo 2 — Entrada vazia / inválida ou tema fora da base
- **Entrada vazia (`""`) ou numérica (`"123"`):**
  `Entrada inválida: digite ao menos uma palavra com 3 letras ou mais (sem apenas números ou símbolos).`
- **Assunto fora dos temas (`"financiamento imobiliário caixa"`):**
  `Não encontrei esse assunto na base de conhecimento. Tente outras palavras (ex.: 'bateria', 'wallbox', 'IPVA') ou use a navegação por temas.`

---

## 8. Plano de Testes e Indicadores de Desempenho
A avaliação completa está documentada em [`docs/plano_testes.md`](docs/plano_testes.md) e automatizada em `src/avaliacao.py`.

- **Total de perguntas testadas:** 12 (6 diretas, 4 variações de frase e 2 fora do escopo)
- **Respostas corretas:** 9
- **Taxa de Acerto:** **75,0%**
- **Tempo Médio de Consulta:** **0,100 ms**
- **Cenários de limitação validados:** entrada vazia (`ENTRADA_INVALIDA`), consulta ambígua com `"bateria"` (`AMBIGUO`) e tema inexistente (`NAO_ENCONTRADO`).
- **Teste de Facilidade de Uso (User Test):** realizado com usuário externo, concluindo tarefas de busca livre, navegação por temas e encadeamento via grafo em menos de 2 minutos.

---

## 9. Conclusões, Limitações e Melhorias Futuras
- **Conclusões:** a combinação de índices invertidos em dicionários, árvore temática e grafo de navegação permitiu respostas instantâneas (< 1 ms) e transparentes, garantindo rastreabilidade das fontes sem depender de APIs externas.
- **Limitações:** 
  - A busca léxica baseada em radicais simples (5 primeiras letras) e `LIMIAR_MINIMO = 2.0` gerou falsos positivos em 2 consultas fora do escopo (`"segunda via"` coincidindo com `"segunda vida"` e `"valor da multa"` coincidindo com `"valor residual"`) e falhou em 1 variação sem sinônimo cadastrado (`"investimento"` para *payback*).
  - A base cobre apenas os temas cadastrados; cada registro tem data de verificação e a
  informação pode ter mudado desde então.
  - A aplicação é informativa e não substitui órgãos oficiais, fabricantes,
  concessionárias de energia ou profissionais habilitados.
- **Melhorias propostas:**
  1. Elevar `LIMIAR_MINIMO` de `2.0` para `3.0` para evitar respostas baseadas em apenas uma coincidência fraca.
  2. Expandir a lista de *stopwords* com termos genéricos (como `"valor"` e `"segunda"`) e adicionar sinônimos às palavras-chave da base.
  3. Salvar um histórico das perguntas sem resposta em um arquivo `.log` para facilitar a expansão futura da base de conhecimento.

---

## 10. Vídeo de Apresentação
- **Link no YouTube:** [LINK_DO_YOUTUBE_AQUI]