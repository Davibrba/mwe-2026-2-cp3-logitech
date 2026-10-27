# 4. Tela do Portal do Cliente (RF10)

A tela de acompanhamento é `UI = f(estado)`. O estado é um único objeto, montado pela carga
inicial (HTTP GET) e atualizado por eventos SSE:

```ts
type EstadoAcompanhamento = {
  carga: 'carregando' | 'erro' | 'pronto';
  conexaoAoVivo: 'conectando' | 'conectado' | 'reconectando';
  pedido?: { id: string; status: 'AGUARDANDO_COLETA' | 'EM_TRANSITO' | 'ENTREGUE' | 'AUSENTE' };
  posicao?: { lat: number; lon: number; registradaEm: string };       // PosicaoAtualizada
  previsao?: { chegadaPrevista: string; prazoPrometido: string };       // Frete
  garantia?: { situacao: 'NO_PRAZO' | 'EM_APURACAO' | 'CREDITO_EMITIDO' | 'SEM_CREDITO';
               motivoSemCredito?: 'TOLERANCIA' | 'CORTESIA' | 'AUSENCIA_COMPROVADA';
               valorCredito?: number; numeroNota?: number };
  saldoCreditos?: number;                                               // SaldoAtualizado
};
```

## Estados da tela

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| **Carregando** | `carga = 'carregando'` | Esqueleto (*skeleton*) do mapa, da previsão e do saldo |
| **Erro na carga** | `carga = 'erro'` | Mensagem "Não foi possível carregar o pedido" e botão **Tentar novamente** |
| **Aguardando coleta** | pedido com status `AGUARDANDO_COLETA`, previsão, saldo; sem posição | Linha do tempo na etapa "Aguardando coleta", previsão de chegada, saldo. Mapa com o endereço de entrega e aviso "O veículo ainda não saiu" |
| **Em trânsito, no prazo** | status `EM_TRANSITO`, posição, previsão ≤ prazo prometido, saldo | Mapa com o veículo e o destino, previsão de chegada em verde, horário da última posição, saldo |
| **Em trânsito, com atraso previsto** | igual ao anterior, mas previsão > prazo prometido | Mesmo que o anterior, previsão em laranja e aviso "Entrega pode atrasar. Se atrasar mais de 2 h, você recebe crédito automaticamente" (texto vem da política do tipo de cliente) |
| **Conexão ao vivo perdida** | `conexaoAoVivo = 'reconectando'` e últimos dados recebidos | Os últimos dados continuam na tela, com selo "Reconectando…" e o horário da última atualização. O `EventSource` reconecta sozinho com `Last-Event-ID` |
| **Entregue no prazo** | status `ENTREGUE`, garantia `NO_PRAZO`, saldo | Linha do tempo concluída, horário da entrega, saldo. Mapa oculto |
| **Entregue com atraso, crédito em apuração** | status `ENTREGUE`, garantia `EM_APURACAO` | Horário da entrega, atraso apurado e "Seu crédito está sendo calculado (até 5 min)" |
| **Entregue com atraso, crédito emitido** | garantia `CREDITO_EMITIDO`, valor, número da nota, saldo atualizado | Cartão "Crédito de R$ X emitido · Nota nº N" e saldo já somado, com destaque breve na mudança |
| **Entregue com atraso, sem crédito** | garantia `SEM_CREDITO` e motivo | Mensagem conforme o motivo: tolerância ("atraso de até 2 h não gera crédito"), Cortesia ("pedido sem frete") ou ausência comprovada ("destinatário ausente no horário da tentativa") |
| **Destinatário ausente** | status `AUSENTE`, posição | Aviso de tentativa de entrega sem sucesso e orientação para reagendar |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>                       // dono do estado (useReducer + EventSource)
  <IndicadorConexao conexaoAoVivo ultimaAtualizacao />
  <EstadoCarga carga onTentarNovamente>               // renderiza Esqueleto | Erro | children
    <LinhaDoTempo status entregueEm />
    <MapaVeiculo posicao destino visivel />
    <PrevisaoChegada previsao status />
    <CartaoGarantia garantia />
      <CreditoEmitido valor numeroNota />             // quando CREDITO_EMITIDO
      <MotivoSemCredito motivo />                     // quando SEM_CREDITO
    <SaldoCreditos saldo />
  </EstadoCarga>
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId` | Faz o GET inicial, abre o `EventSource` de `/pedidos/{id}/eventos`, aplica cada evento num *reducer* puro (`(estado, evento) => estado`) e repassa fatias do estado aos filhos. Único componente com efeito colateral |
| `IndicadorConexao` | `conexaoAoVivo`, `ultimaAtualizacao` | Selo "Ao vivo" / "Reconectando…" com o horário do último evento |
| `EstadoCarga` | `carga`, `onTentarNovamente`, `children` | Mostra esqueleto, erro com botão ou o conteúdo |
| `LinhaDoTempo` | `status`, `entregueEm` | Etapas Coletado → Em trânsito → Entregue/Ausente |
| `MapaVeiculo` | `posicao`, `destino`, `visivel` | Mapa com o marcador do veículo e o destino; oculto após a entrega |
| `PrevisaoChegada` | `previsao`, `status` | Previsão de chegada e cor conforme comparação com o prazo prometido |
| `CartaoGarantia` | `garantia` | Escolhe entre "no prazo", "em apuração", `CreditoEmitido` ou `MotivoSemCredito` |
| `CreditoEmitido` | `valor`, `numeroNota` | Valor e número da nota de crédito |
| `MotivoSemCredito` | `motivo` | Texto explicativo de cada motivo |
| `SaldoCreditos` | `saldo` | Saldo de créditos formatado em reais |

Todos os componentes, exceto `AcompanhamentoPedido`, são puros: mesma prop, mesma saída.
Isso permite testá-los isoladamente com cada estado da tabela acima.

## Origem dos dados

| Dado | Origem | Como chega |
|---|---|---|
| Status do pedido | Pedidos | GET inicial no Portal BFF; mudanças via evento `EntregaConfirmada`/`AusenciaRegistrada` → BFF → SSE `status` |
| Posição do veículo | Telemetria (UDP do veículo a cada 30 s) | Telemetria publica `PosicaoAtualizada` no RabbitMQ → BFF → SSE `posicao` |
| Previsão de chegada e prazo prometido | Frete | GET inicial; o BFF recalcula a previsão quando chega posição nova e envia SSE `previsao` |
| Situação da garantia e crédito | Garantia de Prazo e Faturamento | `AtrasoApurado` e `NotaCreditoEmitida` → BFF → SSE `garantia` |
| Saldo de créditos | Faturamento | GET inicial; `SaldoAtualizado` → BFF → SSE `saldo` |

**Atualização ao vivo.** O navegador abre `new EventSource('/pedidos/{id}/eventos')`. O
Portal BFF assina as filas do RabbitMQ, filtra os eventos daquele pedido e os escreve no
fluxo `text/event-stream`, cada um com `id:` e `event:`. Se a conexão cair, o navegador
reconecta sozinho enviando `Last-Event-ID`, e o BFF reenvia o estado atual para não haver
lacuna. A tela não faz *polling*.
