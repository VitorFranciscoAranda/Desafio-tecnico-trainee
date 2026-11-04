# Etapa 6: revisão dos testes e matriz de cenários

## O que e por quê

Os testes foram escritos junto com cada etapa. Agora é hora de olhar para eles **como um todo** e responder três perguntas:

1. Cada um dos 10 cenários exigidos (T01 a T10) tem pelo menos um teste?
2. Os testes realmente pegam erros, ou só "passam"?
3. Onde está a prova disso para o avaliador?

O critério "Verificação e QA" vale **25%** da nota, então essa revisão é importante. O enunciado pede uma matriz (cenário, esperado, teste, situação), o comando usado e o resumo real da última execução.

## 1. Conferindo cenário por cenário

Rodei `python -m unittest discover -v`, que lista o nome de cada teste, e comparei com a tabela do enunciado. Encontrei dois pontos fracos:

- **T06 (só cabeçalho)** estava testado em pedaços: a leitura devolvia `[]` e o relatório vazio tinha zeros. Faltava um teste que passasse pelo **programa inteiro** e conferisse o JSON gravado.
- **T05 (soma)** conferia o `total_aprovado` recebendo só pedidos válidos, mas ninguém testava a situação real: um pedido **APROVADO porém inválido** passando pela validação e ficando fora da soma.

Por isso acrescentei dois testes de **ponta a ponta** em `tests/test_cli.py`.

### `test_t06_somente_cabecalho`

```python
self.entrada.write_text("pedido_id,cliente,email,valor,data_pedido,status\n", encoding="utf-8")
codigo, _, _ = self.executar("--entrada", ..., "--saida", ..., "--data-referencia", "2026-10-30")
self.assertEqual(codigo, 0)
self.assertEqual(json.loads(self.saida.read_text(encoding="utf-8")), {
    "data_referencia": "2026-10-30",
    "total_registros": 0,
    ...
    "total_aprovado": "0.00",
    "invalidos": [],
})
```
- Cria um CSV só com o cabeçalho, roda o programa e compara o JSON gravado com o dicionário **inteiro** esperado.
- Comparar o dicionário todo de uma vez é mais forte do que conferir campo por campo: se aparecer uma chave a mais, ou faltar uma, o teste falha.
- Também confere o código 0: arquivo só com cabeçalho é **válido**, não é erro.

### `test_t05_aprovado_invalido_fica_fora_da_soma`

```python
"A,Alfa,a@alfa.com,10.00,2026-10-29, aprovado \n"   # válido e aprovado: entra
"B,Beta,b@beta.com,20.00,2026-10-29,PENDENTE\n"      # pendente: fica fora
"C,Gama,c@gama.com,30.00,2026-10-29,CANCELADO\n"     # cancelado: fica fora
"D,Delta,sem-arroba,999.00,2026-10-29,APROVADO\n",   # aprovado, mas inválido: fica fora
```
- Quatro pedidos, um para cada situação do T05. O total esperado é `"10.00"`.
- O pedido D tem um valor alto de propósito (999). Se a soma errasse e incluísse inválidos, o resultado ficaria muito diferente e o erro seria óbvio.
- O pedido A tem `" aprovado "` com espaços e minúsculas. Assim o teste também confere que a normalização (T01) funciona no programa inteiro, e não só na função isolada.
- Os comentários no fim de cada linha explicam a intenção. Quem ler o teste depois entende por que o total deve ser 10.

**Por que testar de ponta a ponta se as funções já têm testes?** Os testes de funções isoladas (testes *unitários*) mostram que cada peça funciona sozinha. O teste de ponta a ponta (teste de *integração*) mostra que as peças funcionam **juntas**: que a saída de uma é a entrada certa da outra.

## 2. Os testes pegam erros? Teste de mutação

Um teste que nunca falha não prova nada. Para conferir, usei uma técnica chamada **teste de mutação**: estragar o código de propósito e ver se os testes reclamam.

Fiz isso numa **cópia** do projeto, numa pasta temporária, para não mexer no código verdadeiro. Para cada mutação, troquei um trecho com o comando `sed` e rodei a suíte:

| Mutação | Trecho original → estragado | Testes que falharam |
|---|---|---|
| Data igual à referência passa a ser recusada | `data > data_referencia` → `data >= data_referencia` | 3 |
| Duplicado só a partir de 3 ocorrências | `quantidade > 1` → `quantidade > 2` | 3 |
| Soma inclui pendentes | `== "APROVADO"` → `!= "CANCELADO"` | 3 |
| Status sem normalizar | a linha do `.upper()` foi removida | 2 |

Nas quatro mutações a suíte **falhou**, que é o resultado desejado: significa que, se alguém quebrar uma dessas regras sem querer no futuro, os testes vão avisar.

Repare na primeira mutação: trocar `>` por `>=` é um erro de **um caractere**, fácil de cometer. É exatamente o tipo de erro que o T04 ("data igual à referência é aceita") existe para pegar.

## 3. A evidência para o avaliador

- **`docs/matriz-testes.md`:** a matriz pedida, com cada cenário T01 a T10, o resultado esperado, os testes correspondentes e a situação. Inclui também os outros testes agrupados por área, o resultado das mutações e as limitações.
- **`docs/evidencias/testes-ultima-execucao.txt`:** a saída **real** do comando `python -m unittest discover -v`, com data e versão do Python. O enunciado diz que mensagens impressas não substituem testes, mas pede o "resumo real da última execução", e é isso que este arquivo registra.
- Esse arquivo vai ser gerado de novo na etapa 8, para refletir a versão final.

## Execução

```
> python -m unittest discover
..............................................................
Ran 62 tests in 0.182s
OK
```

São 62 testes no total: 60 das etapas anteriores e os 2 novos desta etapa.

## Decisões para anotar no registro

- **Dois testes de integração acrescentados (T05 e T06):** os testes unitários não mostravam as peças funcionando juntas nesses dois cenários.
- **Mutação manual em vez de ferramenta:** existem ferramentas que fazem isso automaticamente (como o `mutmut`), mas exigiriam instalar dependências. Quatro mutações manuais nas regras mais importantes bastaram para mostrar que a suíte detecta falhas.
- **Limitações registradas:** sem medição de cobertura, falha de gravação simulada só com "o destino é uma pasta" e testes executados só no Windows.

## Pergunta para conferir o entendimento

Imagine que alguém troque, sem querer, `if erros:` por `if len(erros) > 1:` no `validar_pedidos`. Qual tipo de pedido passaria a ser considerado válido quando não deveria? Algum dos testes atuais pegaria esse erro? Qual?

**Resposta:**
- `if len(erros) > 1:` só considera inválido quem tem **2 ou mais** erros. Um pedido com **exatamente 1 erro** passaria a ser válido. Por exemplo, o PED-003 do enunciado (só o e-mail errado), ou a primeira ocorrência de um ID duplicado que não tem outro problema.
- Pior: esse pedido "válido" teria o valor somado se fosse APROVADO, e o relatório ainda listaria os erros dele em lugar nenhum.
- Fiz essa mutação de verdade numa cópia do código, e **5 testes falharam**:
  - `test_exemplo_do_enunciado` e `test_t08_comando_publicado_gera_json_esperado` (o PED-003 virou válido);
  - `test_t03_duplicado_invalida_todas_as_ocorrencias` e `test_duplicado_detectado_depois_de_remover_espacos` (a ocorrência só com o erro de duplicado virou válida);
  - `test_t05_aprovado_invalido_fica_fora_da_soma` (o pedido D, aprovado e só com o e-mail errado, entrou na soma: o total virou `"1009.00"`).
- Lição: comparar o resultado **inteiro** (o JSON todo, a lista de linhas inválidas) pega erros que um teste mais "frouxo" deixaria passar.
