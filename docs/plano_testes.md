# Plano de Testes e Indicadores de Desempenho

## 1. Metodologia de Avaliação
Para validar o funcionamento do **Assistente de Mobilidade Elétrica**, foi desenvolvido o script `src/avaliacao.py`, que submete 12 consultas padronizadas ao motor de busca (`IndiceConhecimento.buscar`) e mede o tempo de resposta em milissegundos usando `time.perf_counter()`.

As consultas foram divididas em três categorias:
- **6 dúvidas diretas:** perguntas com termos próximos às palavras-chave cadastradas na base.
- **4 variações de frase:** reformulações em linguagem cotidiana, avaliando a remoção de *stopwords* e a comparação por radicais (5 primeiras letras).
- **2 perguntas fora dos 3 temas:** assuntos sem relação com mobilidade elétrica, verificando se o assistente reconhece a ausência de informação sem inventar respostas.

---

## 2. Resultados das 12 Perguntas de Teste

| ID | Categoria | Pergunta de Entrada | Esperado | Obtido | Status | Tempo (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| T01 | Direta | Qual a garantia da bateria? | ID 1 | Resposta Direta (ID 1) | Acerto | 0.124 ms |
| T02 | Direta | Como funciona o carregamento rápido na rodovia? | ID 11 | Resposta Direta (ID 11) | Acerto | 0.125 ms |
| T03 | Direta | Carro elétrico paga IPVA? | ID 14 | Resposta Direta (ID 14) | Acerto | 0.034 ms |
| T04 | Direta | Quais conectores existem no Brasil? | ID 10 | Resposta Direta (ID 10) | Acerto | 0.090 ms |
| T05 | Direta | O síndico pode proibir wallbox no condomínio? | ID 9 | Ambíguo ([ID 9, ID 8]) | Acerto | 0.113 ms |
| T06 | Direta | Carro elétrico pega fogo fácil? | ID 3 | Resposta Direta (ID 3) | Acerto | 0.056 ms |
| T07 | Variação | Preciso trocar óleo e correia dentada? | ID 4 | Resposta Direta (ID 4) | Acerto | 0.118 ms |
| T08 | Variação | Posso passar em rua alagada sem tomar choque? | ID 5 | Resposta Direta (ID 5) | Acerto | 0.128 ms |
| T09 | Variação | Em quanto tempo o investimento se paga rodando muito? | ID 18 | Resposta Direta (ID 7) | Erro | 0.122 ms |
| T10 | Variação | Onde encontro mapa de eletropostos na cidade? | ID 12 | Resposta Direta (ID 12) | Acerto | 0.100 ms |
| T11 | Fora do escopo | Como tirar segunda via do RG? | Não encontrado | Resposta Direta (ID 6) | Erro | 0.074 ms |
| T12 | Fora do escopo | Qual o valor da multa por excesso de velocidade? | Não encontrado | Resposta Direta (ID 16) | Erro | 0.112 ms |

*(Nota: No teste T05, o sistema identificou corretamente o ID 9 como primeira opção e ofereceu desambiguação com o ID 8 — Wallbox Residencial — por ambos tratarem de instalação de carregadores).*

### Indicadores Consolidados
- **Total de perguntas testadas:** 12
- **Respostas corretas:** 9
- **Taxa de Acerto:** 75,0%
- **Tempo Médio de Consulta:** 0,100 ms

---

## 3. Interpretação dos Resultados e Falhas Observadas
A taxa de acerto de **75,0%** e o tempo médio de **0,100 ms** demonstram que a indexação em memória com dicionários e conjuntos é extremamente rápida, porém a sensibilidade do algoritmo de pontuação (`LIMIAR_MINIMO = 2.0`) gerou três comportamentos específicos que explicam os erros:

1. **Falso positivo por radical em `T11` (*"Como tirar segunda via do RG?"*):**
   - A palavra `"segunda"` possui o mesmo radical de 5 letras (`"segun"`) que a palavra-chave `"segunda vida"` do **ID 6** (Reciclagem e Logística Reversa). Como a coincidência de radical atribui +2.0 pontos, atingiu exatamente o `LIMIAR_MINIMO` e retornou um tema não relacionado.
2. **Falso positivo por termo genérico em `T12` (*"Qual o valor da multa por excesso de velocidade?"*):**
   - A palavra `"valor"` aparece no subtema do **ID 16** (*"Depreciação e Valor Residual"*). Como termos no subtema somam +2.0 pontos, o registro atingiu o limiar mínimo de corte mesmo sem tratar de multas de trânsito.
3. **Ausência de sinônimos na variação `T09` (*"Em quanto tempo o investimento se paga rodando muito?"*):**
   - A palavra `"tempo"` pontuou fortemente no **ID 7** (*"tempo de carga"*), enquanto o **ID 18** (Payback) possui apenas termos como `"payback"`, `"ponto de equilibrio"` e `"quilometragem anual"`, não capturando sinônimos como `"investimento"` ou `"retorno"`.

---

## 4. Cenários de Limitação Testados

| Cenário | Entrada Utilizada | Comportamento Obtido | Avaliação |
| :--- | :--- | :--- | :--- |
| **L01 - Entrada vazia** | `"   "` | `ENTRADA_INVALIDA` | Bloqueou a busca e exibiu mensagem orientando o usuário a digitar palavras válidas. |
| **L02 - Pergunta ambígua** | `"bateria"` | `AMBIGUO ([17, 1, 2])` | Identificou múltiplos registros com pontuação próxima e listou opções numeradas para escolha do usuário. |
| **L03 - Tema inexistente** | `"financiamento imobiliário caixa"` | `NAO_ENCONTRADO` | Nenhuma palavra atingiu o limiar mínimo; exibiu aviso de limitação sem inventar dados. |

---

## 5. Comparação dos Modelos de Resposta (Modelo A vs. Modelo B)
Testando a consulta *"Carro elétrico paga IPVA?"* (ID 14):
- **Modelo A (Direto / Técnico):** exibe a orientação resumida, a fonte e a data em 3 linhas, com aviso legal condensado. Ideal para consultas rápidas.
- **Modelo B (Didático / Cidadão):** repete a dúvida, explica o conteúdo de forma acessível, destaca a fonte, exibe o alerta específico de confirmação estadual (`exige_confirmacao_adicional: true`) e apresenta o aviso legal completo.
- **Conclusão:** O **Modelo B** é mais adequado como padrão por reduzir o risco de interpretação equivocada em regras que variam conforme o estado ou município.

---

## 6. Teste de Facilidade de Uso (User Test)
- **Perfil do participante:** 1 usuário externo (motorista interessado na compra de veículo elétrico, sem formação técnica em TI).
- **Roteiro executado:**
  1. Pesquisar livremente sobre isenção de rodízio em São Paulo.
  2. Navegar pelo menu de temas para consultar sobre Wallbox.
  3. Acessar um assunto relacionado sugerido pelo grafo ao final da resposta.
- **Resultados e dificuldades:**
  - Todas as tarefas foram concluídas em menos de 2 minutos.
  - **Dificuldade observada:** na busca textual, o usuário digitou *"rodízio SP"*; como a sigla `"SP"` possui apenas 2 letras e foi tratada de forma neutra frente às palavras-chave, apenas `"rodízio"` contribuiu para a pontuação.

---

## 7. Limitações da Avaliação e Melhorias Futuras
- **Limitações atuais:** a busca léxica baseada em contagem de tokens e radicais simples não compreende contexto semântico nem sinônimos não cadastrados, além de permitir falsos positivos quando palavras genéricas (`"valor"`, `"segunda"`) atingem o limiar mínimo de 2.0 pontos.
- **Melhorias propostas:**
  1. **Ajuste do limiar de corte:** elevar `LIMIAR_MINIMO` de `2.0` para `3.0`, exigindo pelo menos uma palavra-chave exata (+3) ou duas coincidências parciais para evitar falsos positivos fora do escopo.
  2. **Expansão de sinônimos e stopwords:** incluir termos genéricos como `"valor"` e `"segunda"` na lista de `STOPWORDS` e adicionar sinônimos (ex.: `"investimento"`, `"retorno"`) nas `palavras_chave` do registro de Payback.