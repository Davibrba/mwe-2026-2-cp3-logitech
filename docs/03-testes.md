# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 22 (≈ 81%) | Regra de crédito (RF01 a RF04) em todos os valores-limite, regra de ausência comprovada (RF05), escolha de canal e Adapter (RF07), retentativa e fila de falhas (RF08) |
| Integração | 3 (≈ 11%) | Idempotência com banco e broker reais (RF09), unicidade da numeração sob concorrência (RF06, RNF03), não perda da confirmação com o consumidor fora do ar (RNF01) |
| Ponta a ponta | 2 (≈ 8%) | Fluxo completo confirmação → nota de crédito em até 5 min (RNF02), atualização ao vivo do Portal (RF10) |

**Por que essa proporção.** O valor de negócio da Garantia de Prazo está numa regra com
muitos limites (4 faixas × 3 tipos × 2 tetos × arredondamento): cada limite precisa de
dois casos (no limite e logo acima). São regras puras, sem I/O, que rodam em
milissegundos, então concentramos a maior parte dos casos na base. A integração fica
reservada ao que **só existe com infraestrutura real**: unicidade garantida pelo banco
(RF09, RNF03) e durabilidade da fila (RNF01); um dublê nesses casos esconderia exatamente o
que se quer verificar. Os testes ponta a ponta são caros e frágeis (sobem todo o
`compose`), por isso ficam apenas nos dois requisitos que são, por natureza, de fluxo
completo: o tempo total de 5 min (RNF02) e a tela ao vivo (RF10).

**Convenções.** Atraso medido com precisão de segundos; "logo acima do limite" = limite +
1 s. Dinheiro em `Decimal`, arredondamento ao centavo com *half up*. RF08 interpretado
como: 1 tentativa original + até 3 retentativas = no máximo 4 tentativas.

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 2h00min00s | Crédito de R$ 0,00 (limite da tolerância é inclusivo) | Unidade | Nenhum | Regra pura |
| CT03 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h00min01s | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura |
| CT04 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 24h00min00s | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura |
| CT05 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h00min01s | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura |
| CT06 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 72h00min00s | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura |
| CT07 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h00min01s | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura |
| CT08 | RF02 | Cliente Varejo, frete de R$ 1.000,00 | Atraso de 72h00min01s | Crédito de R$ 500,00 (50% coincide com o teto) | Unidade | Nenhum | Regra pura |
| CT09 | RF02 | Cliente Varejo, frete de R$ 1.000,02 | Atraso de 72h00min01s | Crédito de R$ 500,00 (50% = R$ 500,01, limitado ao teto) | Unidade | Nenhum | Regra pura |
| CT10 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atrasos de 2h00min00s e de 2h00min01s | R$ 0,00 e R$ 60,00 (20%) | Unidade | Nenhum | Regra pura |
| CT11 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atrasos de 24h00min00s, 24h00min01s, 72h00min00s e 72h00min01s | R$ 60,00 (20%), R$ 150,00 (50%), R$ 150,00 (50%) e R$ 300,00 (100%) | Unidade | Nenhum | Regra pura |
| CT12 | RF03 | Cliente Corporativo, fretes de R$ 2.000,00 e de R$ 2.000,01 | Atraso de 72h00min01s | R$ 2.000,00 nos dois casos (100% limitado ao teto de R$ 2.000) | Unidade | Nenhum | Regra pura |
| CT13 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 100h | Crédito de R$ 0,00 e apuração marcada para notificar o atraso | Unidade | Nenhum | Regra pura: a decisão de notificar é um dado da apuração |
| CT14 | RF04 | Registro com Varejo, Corporativo e Cortesia | Registrar um tipo novo "Parceiro" (15% acima de 2 h, teto R$ 800) e calcular frete R$ 300,00, atraso 2h00min01s; calcular também um tipo não registrado | Parceiro → R$ 45,00; Varejo e Corporativo continuam com os resultados de CT03 e CT10; tipo não registrado → erro `TipoClienteDesconhecido` | Unidade | Nenhum | O tipo novo é uma política real de teste, não um dublê: verifica-se o resultado, não interações |
| CT15 | RF01 | Prazo prometido 27/10/2026 10:00:00 | Confirmações 27/10/2026 12:00:01 e 27/10/2026 09:30:00 | Atraso de 2h00min01s; atraso de 0 (entrega antecipada não gera atraso negativo) | Unidade | Nenhum | Cálculo puro sobre datas |
| CT16 | RF02 | Cliente Varejo, frete de R$ 123,45 | Atraso de 2h00min01s | Crédito de R$ 12,35 (10% = 12,345, arredondado *half up*) | Unidade | Nenhum | Regra pura |
| CT17 | RF05 | Endereço de entrega conhecido; ausência registrada às 15:00 | Posições: veículo parado a 200 m do endereço de 14:50:00 a 15:00:00 | Ausência comprovada = sim (200 m e 10 min são inclusivos) | Unidade | Nenhum | Regra geoespacial pura sobre uma lista de posições |
| CT18 | RF05 | Mesmo endereço; ausência às 15:00 | (a) parado a 201 m de 14:45 a 15:00; (b) parado a 50 m de 14:50:01 a 15:00:00 (9min59s); (c) parado a 50 m de 15:00 a 15:15 (depois do registro) | Ausência comprovada = não nos três casos | Unidade | Nenhum | Regra pura |
| CT19 | RF05 | Cliente Varejo, frete R$ 300,00, atraso de 30h | `TelemetriaGateway` responde "ausência comprovada" | Crédito de R$ 0,00, motivo `AUSENCIA_COMPROVADA` | Unidade | Stub | O gateway só fornece um dado de entrada; não importa como nem quantas vezes é chamado, só o crédito resultante |
| CT20 | RF07 | Cliente com canal preferido WhatsApp | Notificação "Seu crédito de R$ 75,00 foi emitido" | `WhatsAppAdapter` chama o cliente HTTP do parceiro uma vez, com o payload no formato do parceiro (`to`, `template`, `params`); o canal de e-mail não é chamado | Unidade | Mock | O que se verifica é a interação com a API externa (chamada e formato), não um valor de retorno |
| CT21 | RF08 | Canal configurado para falhar nas 2 primeiras chamadas e aceitar a 3ª | Enviar uma notificação | Envio com estado ENVIADO após 3 tentativas; nada publicado na fila de falhas | Unidade | Spy | Precisa contar as tentativas feitas ao canal sem mudar o comportamento programado dele |
| CT22 | RF08 | Canal configurado para falhar sempre | Enviar uma notificação | Exatamente 4 tentativas (1 + 3 retentativas); estado FALHOU_DEFINITIVO; `NotificacaoFalhou` publicada **uma** vez na fila de falhas | Unidade | Mock | Verifica a interação obrigatória com o publicador da DLQ: a falha final não pode ser descartada em silêncio |
| CT23 | RF09 | Garantia com PostgreSQL e RabbitMQ reais (Testcontainers); Frete e Telemetria simulados por WireMock | Publicar a mesma `EntregaConfirmada` (mesmo `mensagemId`, mesma `entregaId`) duas vezes | 1 linha em `apuracao`; 1 `CreditoConcedido` na outbox; a segunda mensagem recebe *ack* sem efeito | Integração | Stub (Frete e Telemetria) | Frete e Telemetria só fornecem dados; o que se verifica é a unicidade garantida pelo banco, que precisa ser real |
| CT24 | RF06, RNF03 | Faturamento com PostgreSQL real (Testcontainers) | 1.000 `CreditoConcedido` distintos processados em 50 *threads* concorrentes | 1.000 notas; 1.000 números distintos; nenhum repetido; cada número maior que zero | Integração | Nenhum | A concorrência real no banco é o objeto do teste; um dublê do repositório tornaria o teste inútil |
| CT25 | RNF01 | Garantia parada; RabbitMQ e Pedidos no ar | Confirmar uma entrega; depois subir a Garantia | A mensagem continua na fila durável e é consumida; apuração gravada | Integração | Nenhum | Verifica a durabilidade real da fila |
| CT26 | RNF02, RF06 | `docker compose up`; cliente Varejo, frete R$ 300,00, prazo vencido há 30h | POST da confirmação de entrega no Pedidos | Nota de crédito de R$ 75,00 consultável no Faturamento em até 5 min | Ponta a ponta | Stub (só o parceiro WhatsApp e o e-mail, por WireMock) | Serviços externos à LogiTech não podem ser chamados em teste; todo o resto é real |
| CT27 | RF10 | `docker compose up`; tela de acompanhamento aberta no navegador (Playwright) | Publicar `PosicaoAtualizada` e depois `NotaCreditoEmitida` | Mapa e previsão mudam sem recarregar a página em até 5 s; saldo de créditos passa a mostrar R$ 75,00 | Ponta a ponta | Nenhum | Verifica a cadeia real broker → BFF → SSE → React |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Trocar `atraso > 2 h` por `atraso >= 2 h` na faixa de tolerância | CT02 | Com 2h00min00s o mutante concede R$ 30,00 em vez de R$ 0,00 |
| Trocar `atraso <= 72 h` por `atraso < 72 h` na faixa de 25% | CT06 | Com 72h00min00s o mutante concede 50% (R$ 150,00) em vez de 25% (R$ 75,00) |
| Remover o `min(credito, teto)` | CT09 e CT12 | O crédito sairia R$ 500,01 (Varejo) e R$ 2.000,01 (Corporativo) |
| Trocar o fator 2 da política Corporativa por 1 | CT10 e CT11 | Corporativo passaria a receber os percentuais do Varejo (R$ 30,00 em vez de R$ 60,00) |
| Trocar o arredondamento `ROUND_HALF_UP` por `ROUND_HALF_EVEN` | CT16 | 12,345 viraria R$ 12,34 em vez de R$ 12,35 |
| Fazer 3 tentativas no total em vez de 1 + 3 retentativas | CT22 | O teste espera exatamente 4 tentativas antes da fila de falhas |
