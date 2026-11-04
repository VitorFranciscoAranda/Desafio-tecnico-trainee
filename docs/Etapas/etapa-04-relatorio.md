# Etapa 4: relatório JSON

## O que e por quê

As etapas 2 e 3 já entregam duas listas: pedidos válidos e inválidos. Falta transformar isso no **relatório** que o enunciado pede e gravá-lo num arquivo. O `app/relatorio.py` tem três funções, uma para cada tarefa:

1. `total_aprovado`: somar o valor dos pedidos válidos com status APROVADO.
2. `montar_relatorio`: montar o dicionário com os 6 campos do relatório.
3. `gravar_relatorio`: gravar esse dicionário como JSON, com segurança.

Separar **montar** de **gravar** facilita os testes. Dá para conferir o conteúdo do relatório sem criar nenhum arquivo, e conferir a gravação sem se preocupar com as regras.

## Recursos do Python usados

- `decimal.Decimal`: números decimais exatos, para dinheiro.
- `json`: transforma dicionários e listas do Python em texto JSON.
- `pathlib.Path`: criar pastas, renomear e apagar arquivos.
- Exceção própria (`ErroGravacao`), no mesmo estilo do `ErroEstrutural` da etapa 2.

## Por que `Decimal` e não `float`?

O `float` guarda números em binário, e muitos decimais simples não têm representação exata em binário. É como 1/3 em decimal: 0,3333... nunca termina.

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> Decimal("0.10") + Decimal("0.20")
Decimal('0.30')
```

Em dinheiro, esse "erro de centavo" é inaceitável, e o enunciado proíbe somar dinheiro com `float`. Um detalhe importante: o `Decimal` precisa ser criado a partir de um **texto** (`Decimal("0.10")`). Se for criado a partir de um float (`Decimal(0.1)`), ele copia o erro do float. No nosso caso o valor já vem como texto do CSV, então isso acontece naturalmente.

## O código (`app/relatorio.py`)

```python
DUAS_CASAS = Decimal("0.01")
```
- Constante usada para arredondar a 2 casas. Ela funciona como um "modelo" do formato que queremos.

```python
class ErroGravacao(Exception):
    """Não foi possível gravar o relatório no caminho de saída."""
```
- O enunciado pede código de saída diferente de 0 quando não dá para gravar a saída. Com essa exceção, a etapa 5 vai capturar `ErroEstrutural` e `ErroGravacao` e mostrar uma mensagem clara, sem traceback.

### `total_aprovado`

```python
def total_aprovado(validos):
    total = Decimal("0")
    for pedido in validos:
        if pedido["status"] == "APROVADO":
            total += Decimal(pedido["valor"])
    return str(total.quantize(DUAS_CASAS))
```
- Recebe **só os válidos**. Os inválidos nem chegam aqui, então nunca entram na soma, mesmo se forem APROVADO.
- O `status` já está em maiúsculas por causa do `normalizar` da etapa 3, então basta comparar com `"APROVADO"`.
- `Decimal(pedido["valor"])` nunca dá erro aqui, porque a etapa 3 já garantiu que o valor de um pedido válido segue o formato certo.
- `total += ...` é o mesmo que `total = total + ...`.
- `quantize(DUAS_CASAS)` deixa o número com exatamente 2 casas: `Decimal("40")` vira `Decimal("40.00")`. Como todos os valores têm no máximo 2 casas, a soma nunca precisa arredondar nada. O `quantize` aqui serve para **formatar**.
- `str(...)` transforma em texto, porque o enunciado pede `total_aprovado` como string (`"150.50"`). Se não houver aprovados, o total fica `Decimal("0")`, que vira `"0.00"`.
- Escolhi um `for` simples em vez de `sum(...)` com expressão geradora porque fica mais fácil de ler e explicar.

### `montar_relatorio`

```python
def montar_relatorio(validos, invalidos, data_referencia):
    return {
        "data_referencia": data_referencia.isoformat(),
        "total_registros": len(validos) + len(invalidos),
        "registros_validos": len(validos),
        "registros_invalidos": len(invalidos),
        "total_aprovado": total_aprovado(validos),
        "invalidos": invalidos,
    }
```
- `data_referencia.isoformat()` transforma a data em texto `"2026-10-30"`.
- `total_registros` é **calculado** como a soma das outras duas contagens. Assim a regra `total_registros = registros_validos + registros_invalidos` é verdadeira por construção, não tem como falhar.
- `invalidos` já vem pronto da etapa 3, no formato `{linha, pedido_id, erros}`, na ordem do arquivo. Se não houver inválidos, é uma lista vazia `[]`, como pede o enunciado.

### `gravar_relatorio`

```python
def gravar_relatorio(relatorio, caminho):
    caminho = Path(caminho)
    temporario = caminho.with_name(caminho.name + ".tmp")
```
- `with_name` troca só o nome do arquivo, mantendo a pasta. `saida/relatorio.json` vira `saida/relatorio.json.tmp`.
- O enunciado diz para **não publicar um relatório parcial**. Se gravássemos direto em `relatorio.json` e o disco enchesse no meio, ficaria um JSON cortado com o nome do relatório verdadeiro. A solução é gravar num arquivo temporário e só renomear no final.

```python
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
```
- `caminho.parent` é a pasta do arquivo (`saida`).
- `mkdir` cria a pasta. `parents=True` cria também as pastas intermediárias (`a/b/c`), e `exist_ok=True` não dá erro se ela já existir. Isso cumpre "crie a pasta de saída quando necessário".

```python
        with temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
```
- `"w"` abre para escrita, criando ou substituindo o temporário.
- `json.dump` escreve o dicionário como JSON direto no arquivo.
- `ensure_ascii=False` grava os acentos como são (`inválido`). Sem isso, o JSON sairia com `inválido`. Os dois são JSON válido, mas o primeiro é legível para pessoas.
- `indent=2` deixa o JSON com quebras de linha e recuo, fácil de ler.
- `arquivo.write("\n")` termina o arquivo com uma quebra de linha, que é uma boa prática para arquivos de texto.

```python
        temporario.replace(caminho)
```
- Renomeia o temporário para o nome final. Se já existir um relatório antigo com esse nome, ele é **substituído**. O enunciado permite isso ("uma nova execução pode substituir o relatório indicado").
- A troca é feita de uma vez só pelo sistema operacional. Quem abrir o arquivo vê o relatório antigo inteiro ou o novo inteiro, nunca uma mistura.

```python
    except OSError as erro:
        temporario.unlink(missing_ok=True)
        raise ErroGravacao(f"não foi possível gravar o relatório em {caminho}: {erro}")
```
- `OSError` cobre os problemas de sistema: sem permissão, disco cheio, o caminho ser uma pasta etc.
- `unlink(missing_ok=True)` apaga o temporário, se ele existir, para não deixar lixo.
- Depois traduz para `ErroGravacao`, com mensagem em português.

## Os testes (`tests/test_relatorio.py`)

| Teste | O que confere | Cenário |
|---|---|---|
| `test_t05_soma_somente_aprovados` | de 100.00 (aprovado), 50 (pendente), 30 (cancelado) e 0.5 (aprovado), soma só `"100.50"` | T05 |
| `test_t05_sem_erro_de_arredondamento` | `0.10 + 0.20 = "0.30"` | T05 |
| `test_sem_aprovados_da_zero_com_duas_casas` | lista vazia ou sem aprovados dá `"0.00"` | contrato do JSON |
| `test_valor_inteiro_sai_com_duas_casas` | `40` aparece como `"40.00"` | contrato do JSON |
| `test_t05_invalidos_ficam_fora_da_soma` | o total considera só os válidos | T05 |
| `test_contagens_e_data` | contagens, `total_registros` = válidos + inválidos, data em texto | contrato do JSON |
| `test_t06_sem_registros` | relatório completo com zeros, `"0.00"` e `[]` | T06 (a parte do relatório) |
| `test_grava_json_utf8_e_cria_pasta` | cria pastas, grava acentos legíveis, o JSON lido é igual ao original, sem `.tmp` sobrando | gravação |
| `test_substitui_relatorio_anterior` | um relatório antigo é substituído | gravação |
| `test_falha_de_gravacao_gera_erro_controlado` | gravar num caminho que é uma pasta gera `ErroGravacao` e não deixa `.tmp` | falha de gravação |

No teste de gravação, `json.loads(conteudo)` lê o JSON de volta e compara com o dicionário original. Se forem iguais, a gravação está correta.

## Execução

```
> python -m unittest discover
................................................
Ran 48 tests in 0.078s
OK
```

Juntando as etapas 2, 3 e 4 no exemplo do enunciado (o comando `python -m app` com argumentos ainda é a etapa 5, então isto foi feito com um pequeno script de teste):

```json
{
  "data_referencia": "2026-10-30",
  "total_registros": 3,
  "registros_validos": 2,
  "registros_invalidos": 1,
  "total_aprovado": "150.50",
  "invalidos": [
    {
      "linha": 4,
      "pedido_id": "PED-003",
      "erros": [
        "email: formato inválido"
      ]
    }
  ]
}
```

É **exatamente** o "Resultado esperado" do enunciado. A indentação é diferente, mas o enunciado diz que isso não afeta a avaliação.

## Decisões para anotar no registro

- **`Decimal` criado a partir do texto do CSV:** não passa por `float` em nenhum momento.
- **`total_registros` calculado pela soma:** a regra do enunciado vale sempre, por construção.
- **Gravação em arquivo temporário + `replace`:** evita deixar um relatório parcial com o nome do relatório verdadeiro.
- **`ensure_ascii=False` e `indent=2`:** JSON em UTF-8 legível para pessoas.
- **Ainda falta (etapa 5):** se a execução falhar *antes* de gravar, um relatório antigo pode continuar na pasta. O enunciado diz que ele não pode parecer o resultado da execução que falhou. Vamos tratar isso na linha de comando.

## Pergunta para conferir o entendimento

Imagine um arquivo com dois pedidos APROVADO de valor `10.00`, mas um deles tem o e-mail inválido. Qual é o `total_aprovado`? E se trocássemos `validos` por `validos + invalidos` na chamada de `total_aprovado`, o que mudaria (além de dar outro número)?

**Resposta:** o total é `"10.00"` (texto, com duas casas). Trocar para `validos + invalidos` **não** daria 20: o programa **quebraria** com `KeyError: 'status'`. Os itens de `invalidos` têm só `linha`, `pedido_id` e `erros`, sem `status` nem `valor`. E mesmo que tivessem, um valor inválido como `"abc"` faria o `Decimal` falhar. Moral: cada lista tem um formato próprio, e `total_aprovado` só funciona com pedidos válidos, porque a etapa 3 já garantiu que o valor deles é um número correto.
