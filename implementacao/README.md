# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: **Python 3.10+** com **pytest** (código em
  [`python/`](python/))
- Comando para executar os testes:
  ```bash
  cd implementacao/python && pip install pytest && python -m pytest
  ```
- Casos do plano implementados (IDs): **CT01 a CT16** (regras do RF01 ao RF04)
- Organização:
  - `src/garantia/credito.py`: `PoliticaDeCredito` (Strategy), `PoliticaPorFaixas`
    (Varejo e Corporativo, faixas como tabela de dados), `PoliticaCortesia` e
    `RegistroDePoliticas` (tipo novo = `registrar`, sem editar os existentes, RF04)
  - `src/garantia/atraso.py`: cálculo do atraso (RF01)
- Sequência TDD no histórico: cada `test:` (vermelho) é seguido pelo `feat:` que o faz
  passar; há um `refactor:` (faixas como tabela) feito com os testes verdes. CT08 já passou
  no commit de teste porque coincide com o teto; o vermelho daquele ciclo veio de CT09.
- Mutantes do plano (`docs/03-testes.md`) aplicados à mão no código e confirmados como
  detectados pelos testes.
- Saída da última execução dos testes:

```
============================= test session starts ==============================
platform linux -- Python 3.13.17, pytest-9.2.0, pluggy-1.7.0
configfile: pyproject.toml
testpaths: tests
collected 19 items

tests/test_atraso.py::test_ct15_atraso_e_a_diferenca_entre_confirmacao_e_prazo_prometido PASSED [  5%]
tests/test_atraso.py::test_ct15_entrega_antecipada_nao_gera_atraso_negativo PASSED [ 10%]
tests/test_credito.py::test_ct01_varejo_atraso_abaixo_da_tolerancia_nao_gera_credito PASSED [ 15%]
tests/test_credito.py::test_ct02_varejo_atraso_exatamente_no_limite_da_tolerancia_nao_gera_credito PASSED [ 21%]
tests/test_credito.py::test_ct03_varejo_um_segundo_acima_da_tolerancia_gera_10_porcento PASSED [ 26%]
tests/test_credito.py::test_ct04_varejo_exatamente_24h_ainda_gera_10_porcento PASSED [ 31%]
tests/test_credito.py::test_ct05_varejo_um_segundo_acima_de_24h_gera_25_porcento PASSED [ 36%]
tests/test_credito.py::test_ct06_varejo_exatamente_72h_ainda_gera_25_porcento PASSED [ 42%]
tests/test_credito.py::test_ct07_varejo_um_segundo_acima_de_72h_gera_50_porcento PASSED [ 47%]
tests/test_credito.py::test_ct08_varejo_50_porcento_coincide_com_o_teto PASSED [ 52%]
tests/test_credito.py::test_ct09_varejo_credito_um_centavo_acima_do_teto_e_limitado_a_500 PASSED [ 57%]
tests/test_credito.py::test_ct16_varejo_credito_arredondado_ao_centavo_half_up PASSED [ 63%]
tests/test_credito.py::test_ct10_corporativo_tolerancia_igual_e_percentual_dobrado_na_primeira_faixa PASSED [ 68%]
tests/test_credito.py::test_ct11_corporativo_percentuais_dobrados_nos_limites_das_faixas PASSED [ 73%]
tests/test_credito.py::test_ct12_corporativo_credito_limitado_ao_teto_de_2000 PASSED [ 78%]
tests/test_credito.py::test_ct13_cortesia_nao_recebe_credito_mas_e_notificada_do_atraso PASSED [ 84%]
tests/test_registro_de_politicas.py::test_ct14_tipo_novo_e_registrado_sem_alterar_os_tipos_existentes PASSED [ 89%]
tests/test_registro_de_politicas.py::test_ct14_registro_de_tipo_novo_nao_vaza_para_o_registro_padrao PASSED [ 94%]
tests/test_registro_de_politicas.py::test_ct14_tipo_nao_registrado_gera_erro PASSED [100%]

============================== 19 passed in 0.03s ==============================
```
