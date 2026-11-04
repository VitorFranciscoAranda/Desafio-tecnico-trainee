# Etapa 7: dados de exemplo e de demonstração

## O que e por quê

O enunciado pede três entregas de dados:

1. **`dados/pedidos.csv`:** o exemplo com os três pedidos do enunciado (criado na etapa 5).
2. **Um CSV de demonstração** com pelo menos 12 pedidos fictícios, cobrindo: pedidos válidos, duplicidade, vários erros na mesma linha, valor inválido, data impossível e os três status.
3. **O relatório da demonstração** e o **comando exato** usado para gerá-lo, com data de referência explícita.

A demonstração serve como uma **vitrine**: em um só arquivo, o avaliador vê o programa lidando com todos os casos do contrato.

## Arquivos criados

| Arquivo | Conteúdo |
|---|---|
| `dados/pedidos.csv` | os 3 pedidos do enunciado |
| `dados/pedidos_demonstracao.csv` | 19 pedidos fictícios + 1 linha em branco |
| `saida/relatorio.json` | relatório do exemplo |
| `saida/relatorio_demonstracao.json` | relatório da demonstração |

## Comandos exatos

```
python -m app --entrada dados/pedidos.csv --saida saida/relatorio.json --data-referencia 2026-10-30
python -m app --entrada dados/pedidos_demonstracao.csv --saida saida/relatorio_demonstracao.json --data-referencia 2026-10-30
```

A data de referência é a mesma do enunciado (2026-10-30), para que o resultado seja sempre o mesmo, não importa o dia em que o comando for executado.

## Como montei o arquivo de demonstração

Planejei **cada linha com um objetivo**: um caso do enunciado por linha, para ficar fácil conferir. Os nomes e e-mails são fictícios.

| Linha | Pedido | O que testa | Esperado |
|---|---|---|---|
| 1 | cabeçalho | | |
| 2 | PED-101 | aprovado normal, **mas o ID se repete na linha 20** | inválido: duplicado |
| 3 | PED-102 | status em minúsculas (`pendente`), valor com 1 casa (`89.9`) | válido |
| 4 | PED-103 | espaços nas pontas de vários campos, `  Aprovado  `, valor sem casas (`1200`) | válido, aprovado |
| 5 | PED-104 | status CANCELADO | válido |
| 6 | PED-105 | nome entre aspas com vírgula (`"Silva, Eduardo"`), valor `0.10` | válido, aprovado |
| 7 | PED-106 | data **igual** à referência, valor `0.20` | válido, aprovado |
| 8 | PED-107 | primeira ocorrência de duplicado | inválido: duplicado |
| 9 | PED-107 | segunda ocorrência de duplicado | inválido: duplicado |
| 10 | (em branco) | linha totalmente em branco | ignorada |
| 11 | PED-108 | valor com vírgula (`"12,50"`) | inválido: valor |
| 12 | PED-109 | valor negativo (`-30.00`) | inválido: valor |
| 13 | PED-110 | data impossível (`2026-02-30`) | inválido: data |
| 14 | PED-111 | data futura (`2026-11-15`) | inválido: data |
| 15 | PED-112 | **vários erros**: cliente vazio, e-mail com espaço e sem `@`, valor `abc`, data `30/10/2026`, status `ENVIADO` | inválido: 5 erros |
| 16 | PED-113 | e-mail com dois `@` e valor com 3 casas | inválido: 2 erros |
| 17 | (vazio) | ID vazio | inválido: só "obrigatório" |
| 18 | PED-114 | valor zero | inválido: valor |
| 19 | `,,,,,` | linha só com separadores | inválido: 6 erros |
| 20 | PED-101 | duplicado da linha 2 **e** e-mail `paulo@` | inválido: e-mail + duplicado |
| 21 | ped-114 | mesmo texto de PED-114, mas em minúsculas | válido (não é duplicado) |

Alguns detalhes de escrita do CSV:
- Na linha 11, o valor `12,50` precisa estar **entre aspas**. Sem aspas, a vírgula seria lida como separador, a linha ficaria com 7 campos, e o programa pararia com **erro estrutural**. Com aspas, é um campo só, que a validação recusa por usar vírgula.
- Na linha 4, os espaços estão fora de aspas de propósito, para mostrar a normalização.

## Conferindo o resultado à mão

Antes de olhar o relatório, calculei o resultado esperado:

- **Total de registros:** 21 linhas − 1 cabeçalho − 1 linha em branco = **19**.
- **Válidos:** PED-102, PED-103, PED-104, PED-105, PED-106 e ped-114 = **6**.
- **Inválidos:** 19 − 6 = **13**.
- **Total aprovado:** só os válidos com status APROVADO, que são PED-103 (1200), PED-105 (0.10) e PED-106 (0.20). 1200 + 0.10 + 0.20 = **1200.30**.
  - PED-101 (250 e 500), PED-107 (99.99), PED-108, PED-110, Nicolas e PED-114 também são APROVADO, mas são inválidos e ficam fora.

## Execução real

```
> python -m app --entrada dados/pedidos_demonstracao.csv --saida saida/relatorio_demonstracao.json --data-referencia 2026-10-30
Conferência concluída.
  Data de referência:   2026-10-30
  Total de registros:   19
  Registros válidos:    6
  Registros inválidos:  13
  Total aprovado:       1200.30
  Relatório gravado em: saida\relatorio_demonstracao.json
```

**Bateu com o cálculo à mão.** O relatório lista os 13 inválidos na ordem das linhas (2, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20). Alguns trechos:

```json
{
  "linha": 15,
  "pedido_id": "PED-112",
  "erros": [
    "cliente: obrigatório",
    "email: formato inválido",
    "valor: formato inválido (use 10, 10.5 ou 10.50)",
    "data_pedido: formato inválido (use AAAA-MM-DD)",
    "status: inválido (use PENDENTE, APROVADO ou CANCELADO)"
  ]
},
{
  "linha": 17,
  "pedido_id": "",
  "erros": ["pedido_id: obrigatório"]
},
{
  "linha": 20,
  "pedido_id": "PED-101",
  "erros": ["email: formato inválido", "pedido_id: duplicado no arquivo"]
}
```

Repare:
- **Linha 15:** os 5 erros independentes foram acumulados, e a linha conta como **um** inválido.
- **Linha 17:** ID vazio recebe só "obrigatório", sem erro de duplicado, mesmo com a linha 19 também tendo ID vazio.
- **Linha 20:** o duplicado mostra também o outro erro (T03).
- **Linha 12:** `-30.00` aparece como "formato inválido", e não como "deve ser maior que zero". O sinal de menos já é barrado pela regex, antes de o número ser criado.
- **Linha 21:** `ped-114` não foi marcado como duplicado de `PED-114`.

## Um teste novo para proteger a entrega

Acrescentei `test_relatorio_de_demonstracao_entregue_esta_atualizado` em `tests/test_cli.py`:

```python
entregue = RAIZ_DO_PROJETO / "saida" / "relatorio_demonstracao.json"
codigo, _, _ = self.executar("--entrada", str(RAIZ_DO_PROJETO / "dados" / "pedidos_demonstracao.csv"),
                             "--saida", str(self.saida), "--data-referencia", "2026-10-30")
self.assertEqual(json.loads(self.saida.read_text(encoding="utf-8")),
                 json.loads(entregue.read_text(encoding="utf-8")))
```

- Ele gera o relatório da demonstração de novo, numa pasta temporária, e compara com o arquivo entregue em `saida/`.
- **Risco coberto:** se alguém mudar uma regra ou uma mensagem de erro e esquecer de gerar o relatório de novo, o arquivo entregue ficaria desatualizado, mostrando um resultado que o código já não produz. Esse teste falharia e avisaria.
- Ele grava numa pasta temporária, e não em `saida/`, para que rodar os testes nunca altere os arquivos entregues.

```
> python -m unittest discover
Ran 63 tests in 0.200s
OK
```

## Decisões para anotar no registro

- **Uma linha por caso:** facilita conferir e explicar a demonstração.
- **Data de referência fixa (2026-10-30):** o resultado é reprodutível em qualquer dia.
- **19 registros em vez de 12:** o mínimo não cabia todos os casos do contrato (duplicidade com outro erro, ID vazio, linha só com separadores, maiúsculas no ID).
- **Teste que compara o relatório entregue:** garante que a evidência entregue corresponde ao código.

## Pergunta para conferir o entendimento

Se você tirasse as aspas de `"12,50"` na linha 11, o que aconteceria ao rodar o comando da demonstração? Qual seria o código de saída, e o `saida/relatorio_demonstracao.json` seria alterado?

**Resposta (testada numa cópia do arquivo):**
- Sem aspas, a vírgula de `12,50` vira um **separador**. A linha 11 fica com 7 campos, e o cabeçalho tem 6.
- Isso é **erro estrutural**, não erro de pedido. O `ler_pedidos` lança `ErroEstrutural` e o processamento inteiro para:
  ```
  Erro: linha 11: esperados 6 campos, encontrados 7
  Aviso: nenhum relatório foi gravado. O arquivo saida\relatorio_demonstracao.json é de uma execução anterior e não corresponde a esta.
  ```
- **Código de saída: 1.**
- **O relatório não é alterado.** Conferi com um *hash* (uma "impressão digital" do arquivo) antes e depois, e deu igual. A gravação nem é tentada, porque o erro acontece na leitura, e o relatório antigo continua lá, com o aviso de que não é desta execução.
- Moral: a mesma informação ("12,50") pode ser um erro de **negócio** (com aspas: só aquele pedido fica inválido) ou um erro de **estrutura** (sem aspas: o arquivo todo é recusado). Quem decide é o formato CSV.
