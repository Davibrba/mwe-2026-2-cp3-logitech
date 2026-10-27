# 5. Uso de assistentes de IA

A dupla usou o **Claude Code** (assistente de IA da Anthropic) como apoio em todas as
entregas, a partir do enunciado do `README.md`. O assistente redigiu os rascunhos dos
documentos e conduziu os ciclos de TDD; os commits de autoria do assistente trazem a linha
`Co-Authored-By: Claude`. A dupla revisou o material e é responsável pelo conteúdo final.

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| Todas | "Realize a atividade proposta no README.md" | Preencher `docs/01` a `docs/04`, implementar a regra do RF02 ao RF04 em TDD e registrar o uso de IA | Aceito como ponto de partida | Cobre todas as entregas avaliadas no tempo da atividade |
| 1. Domínio | Bounded contexts e responsável único por requisito | Criar o contexto **Garantia de Prazo** como *core domain*, separado de Pedidos e Faturamento | Aceito | A regra de crédito tem linguagem própria (atraso, faixa, teto) e muda por motivos comerciais, não fiscais nem logísticos |
| 1. Domínio | Onde fica o RF05 | Colocar a comprovação de ausência no **Rastreamento**, e não na Garantia | Aceito | A regra é geoespacial (200 m, 10 min) e depende do histórico de posições; a Garantia só consome "sim/não" |
| 1. Domínio | Onde fica o RF05 | Alternativa considerada: regra dentro da Garantia, lendo posições da Telemetria | Descartado | Faria a Garantia conhecer coordenadas e duplicar o modelo do Rastreamento |
| 2. Arquitetura | Protocolos | UDP para telemetria; AMQP (RabbitMQ, fila durável) para a confirmação; SSE para o Portal | Aceito | UDP: tolera perda e substitui o pacote perdido (RNF01); fila durável: não perde a confirmação (RNF01); SSE: fluxo só servidor → cliente com reconexão automática (RF10) |
| 2. Arquitetura | Protocolo do Portal | WebSocket | Descartado | Não há mensagens do navegador para o servidor; SSE é mais simples e roda sobre HTTP comum |
| 2. Arquitetura | Padrões | Strategy + registro (RF04), Adapter (RF07), Decorator de retentativa + DLQ (RF08), Idempotent Consumer (RF09), Outbox | Aceito | Cada padrão está ligado a um requisito que o pede |
| 2. Arquitetura | Ponto sem padrão | Não usar Chain of Responsibility nas faixas nem Singleton no gerador de número | Aceito | Faixas são dados; Singleton não garante unicidade com várias réplicas |
| 2. Arquitetura | RF06/RNF03 | `SEQUENCE` do PostgreSQL com `UNIQUE`, e o aviso de que `SEQUENCE` pode ter lacunas | Aceito, com a alternativa de tabela contador documentada | O RF06 exige "nunca repetido"; lacunas só seriam problema se o fiscal exigir |
| 3. Testes | Valores-limite | Precisão de segundos: testar no limite e no limite + 1 s | Aceito | Torna os limites exatos e detecta troca de `<=` por `<` |
| 3. Testes | Interpretação do RF08 | 1 tentativa original + 3 retentativas = 4 tentativas | Aceito, registrado no plano | O texto diz "retentada até 3 vezes", ou seja, 3 tentativas além da original |
| 3. Testes | Arredondamento | Arredondar ao centavo com *half up* e criar o CT16 para isso | Aceito | O enunciado não define; *half up* é o arredondamento comercial usual, e o CT16 torna a escolha explícita |
| 4. Portal | Tela como função do estado | Um único objeto de estado, *reducer* puro para eventos SSE e componentes filhos puros | Aceito | Facilita testar cada estado isoladamente |
| 5. Implementação | Linguagem | Python com pytest | Aceito | Menor quantidade de código de infraestrutura; `Decimal` resolve dinheiro sem dependências |
| 5. Implementação | Ordem dos ciclos | Começar com `if` por tipo e só refatorar para Strategy quando o CT14 (RF04) exigir | Aceito | Mantém o TDD honesto: o padrão aparece quando um teste o motiva |
| 5. Implementação | Verificação | Aplicar à mão os mutantes do plano e confirmar que os testes falham | Aceito | Confirma que a tabela de mutantes do plano é verdadeira |
