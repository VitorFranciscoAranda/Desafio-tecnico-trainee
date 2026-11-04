# Etapa 5: linha de comando (CLI)

## O que e por quê

As etapas 2, 3 e 4 criaram as peças: ler, validar e gravar o relatório. Até agora, para juntá-las, era preciso escrever um script. Nesta etapa, o `app/__main__.py` passa a ser o **coordenador**. Ele:

1. lê os argumentos do terminal (`--entrada`, `--saida`, `--data-referencia`);
2. impede que a entrada e a saída sejam o mesmo arquivo;
3. chama as peças na ordem: ler → validar → montar → gravar;
4. mostra o resumo no terminal, ou uma mensagem de erro clara;
5. devolve o **código de saída** certo para o sistema operacional.

Repare que o `__main__.py` **não tem regra de negócio nenhuma**. Ele não sabe o que é um e-mail válido nem como somar valores. Ele só chama quem sabe. Se a regra do e-mail mudar, este arquivo não muda.

## Recursos do Python usados

- `argparse`: módulo nativo que lê argumentos do terminal e gera o `--help` sozinho.
- `sys.stderr`: a "saída de erros" do terminal, separada da saída normal (`sys.stdout`).
- `sys.exit(codigo)`: encerra o programa devolvendo um número ao sistema operacional.
- `Path.samefile`: confere se dois caminhos são o mesmo arquivo no disco.
- `try/except` com **várias exceções** ao mesmo tempo.

## Códigos de saída

Todo programa, ao terminar, devolve um número ao sistema operacional. Scripts e ferramentas automáticas usam esse número para saber se deu certo, sem precisar ler o texto.

| Código | Quando |
|---|---|
| `0` | Relatório gravado com sucesso, **mesmo que haja pedidos inválidos**. Pedido inválido é resultado normal da conferência, não falha do programa. |
| `1` | Falha no processamento: arquivo inexistente, erro estrutural, codificação inválida, falha de gravação, entrada igual à saída. |
| `2` | Argumentos inválidos: falta `--entrada` ou `--saida`, data de referência inválida. Este código é o padrão do `argparse`. |

No PowerShell, dá para ver o código da última execução com `$LASTEXITCODE`.

## O código (`app/__main__.py`), parte por parte

### `data_valida`

```python
def data_valida(texto):
    try:
        if not PADRAO_DATA.fullmatch(texto):
            raise ValueError
        return date.fromisoformat(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"data inválida '{texto}' (use uma data real no formato AAAA-MM-DD)")
```
- O `argparse` recebe tudo como texto. Com `type=data_valida`, ele chama esta função para **converter** o texto numa `date`.
- Reaproveitamos o `PADRAO_DATA` da etapa 3, para exigir o mesmo formato exato `AAAA-MM-DD` dos pedidos.
- Se o formato estiver errado, lançamos `ValueError` de propósito. Assim os dois problemas (formato errado e data inexistente como 30/02) caem no mesmo `except`.
- `ArgumentTypeError` é a exceção que o `argparse` entende. Ele mostra a mensagem e encerra com código 2.

### `criar_parser`

```python
parser = argparse.ArgumentParser(prog="python -m app", description=..., epilog=...)
parser.add_argument("--entrada", required=True, type=Path, help="...")
parser.add_argument("--saida", required=True, type=Path, help="...")
parser.add_argument("--data-referencia", type=data_valida, help="...")
```
- `prog`, `description` e `epilog` são os textos do `--help`: o nome do comando, a descrição no topo e o exemplo no final.
- `required=True` torna o argumento obrigatório. Se faltar, o `argparse` mostra o erro sozinho.
- `type=Path` já converte o texto num `Path`.
- `--data-referencia` não tem `required`, então é opcional. Se não for informado, o valor fica `None`.
- O `argparse` troca o hífen por sublinhado: `--data-referencia` vira `argumentos.data_referencia`, porque hífen não pode aparecer em nome de variável.
- O `--help` é criado automaticamente a partir dos textos `help=`.

### `mesmo_arquivo`

```python
def mesmo_arquivo(entrada, saida):
    return entrada.exists() and saida.exists() and entrada.samefile(saida)
```
- Comparar os textos dos caminhos não basta. `dados\pedidos.csv`, `.\dados\pedidos.csv`, `saida\..\dados\pedidos.csv` e `DADOS\PEDIDOS.CSV` (no Windows) são todos o **mesmo arquivo**.
- `samefile` pergunta ao sistema operacional se os dois caminhos levam ao mesmo arquivo no disco, e assim resolve todos esses casos.
- `samefile` dá erro se algum dos arquivos não existir, por isso conferimos `exists()` antes.
- O `and` para no primeiro `False` (isso se chama *avaliação em curto-circuito*). Então o `samefile` só roda quando os dois existem.
- Se a saída ainda não existe, ela não pode ser o arquivo de entrada, então não há perigo.

### `falhar`

```python
def falhar(mensagem, saida=None):
    print(f"Erro: {mensagem}", file=sys.stderr)
    if saida is not None and saida.exists():
        print(f"Aviso: nenhum relatório foi gravado. O arquivo {saida} é de uma execução "
              "anterior e não corresponde a esta.", file=sys.stderr)
    return 1
```
- `file=sys.stderr` manda a mensagem para a saída de **erros**. Assim, quem redirecionar a saída normal para um arquivo continua vendo os erros na tela.
- O **aviso** resolve a regra "um relatório anterior não deve ser apresentado como resultado da execução que falhou". Se já existir um relatório antigo no caminho de saída, avisamos claramente que ele **não** é desta execução.
- `saida=None` é um **parâmetro com valor padrão**: quem chama pode omitir. No caso de entrada igual à saída, omitimos, porque ali a "saída" é o próprio CSV e o aviso não faria sentido.
- Devolve `1`, o código de falha.

### `imprimir_resumo`

Mostra no terminal as contagens, o total aprovado e o caminho do relatório, como pede o RF06 do enunciado. São só `print`s com f-strings, alinhados com espaços para ficar fácil de ler.

### `main`: a coordenação

```python
def main(argv=None):
    hoje = date.today()  # obtida uma única vez, no início da execução
    argumentos = criar_parser().parse_args(argv)
    data_referencia = argumentos.data_referencia or hoje
```
- `date.today()` pega a data do computador **uma única vez**, no início, como pede o enunciado. Se o programa rodasse perto da meia-noite e pegasse a data duas vezes, poderia usar dias diferentes em partes diferentes.
- `parse_args(argv)` lê os argumentos. Quando `argv` é `None`, o `argparse` usa os argumentos reais do terminal (`sys.argv`). Nos testes, passamos uma lista, como `["--entrada", "x.csv", ...]`, sem precisar abrir um terminal.
- `argumentos.data_referencia or hoje`: o `or` devolve o primeiro valor "verdadeiro". Se a data não foi informada (`None`), usa `hoje`.

```python
    if mesmo_arquivo(argumentos.entrada, argumentos.saida):
        return falhar("--entrada e --saida apontam para o mesmo arquivo; escolha outro caminho para a saída")
```
- Esta conferência vem **antes** de qualquer leitura ou gravação. Assim o arquivo de entrada nunca corre o risco de ser sobrescrito.

```python
    try:
        registros = ler_pedidos(argumentos.entrada)
        validos, invalidos = validar_pedidos(registros, data_referencia)
        relatorio = montar_relatorio(validos, invalidos, data_referencia)
        gravar_relatorio(relatorio, argumentos.saida)
    except (ErroEstrutural, ErroGravacao) as erro:
        return falhar(str(erro), argumentos.saida)
```
- As quatro chamadas são o **fluxo inteiro** do programa. Dá para explicar o projeto todo a partir destas 4 linhas.
- `except (ErroEstrutural, ErroGravacao)` captura qualquer um dos dois tipos, usando uma tupla de exceções.
- Lembra por que criamos as exceções próprias nas etapas 2 e 4? É aqui que elas compensam: o coordenador só precisa conhecer **dois** tipos de erro, e não `UnicodeDecodeError`, `csv.Error`, `OSError` etc.
- `str(erro)` pega a mensagem em português que escrevemos lá.
- Se um erro acontecer na leitura, a gravação nem é tentada. Nenhum relatório parcial é criado.
- Não capturamos `Exception` em geral, de propósito. Um erro inesperado seria um **bug**, e esconder bugs atrás de uma mensagem genérica dificultaria encontrá-los.

```python
    imprimir_resumo(relatorio, argumentos.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
- Só imprime o resumo depois que o relatório foi gravado com sucesso.
- `sys.exit(main())` entrega ao sistema operacional o código que `main` devolveu.

## Os testes (`tests/test_cli.py`)

Há duas formas de testar a CLI, e usamos as duas:

1. **Chamar `main([...])` direto** com uma lista de argumentos. É rápido, e o método auxiliar `executar` captura o que seria impresso usando `redirect_stdout` e `redirect_stderr`, que desviam os `print`s para um `io.StringIO` (um "arquivo" na memória).
2. **Rodar o comando de verdade** com `subprocess.run([sys.executable, "-m", "app", ...])`. É o T08: prova que o comando publicado no README funciona como um usuário o usaria. `sys.executable` é o caminho do Python que está rodando os testes.

Quando o `argparse` encontra erro, ou com `--help`, ele chama `sys.exit`, que lança `SystemExit`. Por isso esses testes usam `assertRaises(SystemExit)` e conferem o `.code`.

| Teste | O que confere | Cenário |
|---|---|---|
| `test_t08_comando_publicado_gera_json_esperado` | o comando real grava o JSON idêntico ao do enunciado, código 0, resumo com total e caminho | T08 |
| `test_sem_data_de_referencia_usa_hoje` | sem `--data-referencia`, o relatório usa a data de hoje | data padrão |
| `test_entrada_nao_e_modificada` | os bytes do CSV são iguais antes e depois | nunca modificar a entrada |
| `test_t07_arquivo_inexistente` | código ≠ 0, mensagem clara, sem traceback, sem relatório | T07 |
| `test_t07_coluna_obrigatoria_ausente` | código ≠ 0, mensagem cita `email`, sem relatório | T07 |
| `test_t09_codificacao_invalida` | arquivo em Latin-1: código ≠ 0, mensagem cita UTF-8 | **T09 (nosso)** |
| `test_t10_entrada_igual_a_saida` | código ≠ 0 e o CSV continua intacto | **T10 (nosso)** |
| `test_t10_mesmo_arquivo_escrito_de_outro_jeito` | `saida/../pedidos.csv` também é detectado | **T10 (nosso)** |
| `test_falha_avisa_que_relatorio_antigo_nao_vale` | com relatório antigo na pasta, a falha avisa que ele não é desta execução | relatório anterior |
| `test_falha_ao_gravar` | saída que é uma pasta: código ≠ 0 e mensagem clara | falha de gravação |
| `test_help` | `--help` encerra com código 0 | `--help` |
| `test_saida_obrigatoria` | sem `--saida`: código ≠ 0 | argumentos obrigatórios |
| `test_data_de_referencia_invalida` | `2026-02-30`, `30/10/2026` e `20261030` são recusadas | data de referência real |

**Os dois cenários escolhidos por nós** (o enunciado pede que expliquemos o risco de cada um):
- **T09, codificação inválida:** arquivos exportados do Excel ou do Bloco de Notas antigo costumam vir em Latin-1/ANSI. O risco é o programa quebrar com um traceback ou, pior, ler acentos errados em silêncio.
- **T10, entrada igual à saída:** um erro de digitação no terminal poderia **apagar os dados originais**, substituindo o CSV pelo relatório. É o tipo de erro que não tem volta, por isso vale um teste.

Também removi o teste `test_main_retorna_zero` da etapa 1. Agora `main()` exige argumentos, e ele ficou coberto pelos testes acima.

## Execução real no PowerShell

```
> python -m app --help
usage: python -m app [-h] --entrada ENTRADA --saida SAIDA
                     [--data-referencia DATA_REFERENCIA]

Confere um arquivo CSV de pedidos e gera um relatório JSON.

options:
  -h, --help            show this help message and exit
  --entrada ENTRADA     caminho do arquivo CSV de pedidos (UTF-8)
  --saida SAIDA         caminho do relatório JSON; a pasta é criada se não
                        existir
  --data-referencia DATA_REFERENCIA
                        data AAAA-MM-DD; pedidos com data posterior são
                        inválidos (padrão: a data de hoje no computador)

Exemplo: python -m app --entrada dados/pedidos.csv --saida
saida/relatorio.json --data-referencia 2026-10-30
```

Com o exemplo do enunciado (os caminhos foram encurtados aqui para facilitar a leitura; o teste foi feito numa pasta temporária):
```
> python -m app --entrada pedidos.csv --saida saida\relatorio.json --data-referencia 2026-10-30
Conferência concluída.
  Data de referência:   2026-10-30
  Total de registros:   3
  Registros válidos:    2
  Registros inválidos:  1
  Total aprovado:       150.50
  Relatório gravado em: saida\relatorio.json
> $LASTEXITCODE
0
```

Falhas:
```
> python -m app --entrada nao_existe.csv --saida saida\relatorio.json
Erro: arquivo de entrada não encontrado: nao_existe.csv
Aviso: nenhum relatório foi gravado. O arquivo saida\relatorio.json é de uma execução anterior e não corresponde a esta.
(código 1)

> python -m app --entrada pedidos.csv --saida pedidos.csv
Erro: --entrada e --saida apontam para o mesmo arquivo; escolha outro caminho para a saída
(código 1)

> python -m app --entrada pedidos.csv --saida x.json --data-referencia 2026-02-30
python -m app: error: argument --data-referencia: data inválida '2026-02-30' (use uma data real no formato AAAA-MM-DD)
(código 2)

> python -m app --entrada pedidos.csv
python -m app: error: the following arguments are required: --saida
(código 2)
```

Testes:
```
> python -m unittest discover
Ran 60 tests in 0.204s
OK
```

## Decisões para anotar no registro

- **`__main__.py` só coordena:** nenhuma regra de negócio fica nele.
- **Códigos 0, 1 e 2:** 0 sucesso (mesmo com inválidos), 1 falha de processamento, 2 argumentos inválidos (padrão do `argparse`).
- **`samefile` para detectar entrada igual à saída:** cobre caminhos relativos, `..` e diferenças de maiúsculas no Windows.
- **Relatório antigo:** em caso de falha, o programa **não apaga** o relatório anterior, porque apagar arquivos do usuário sem pedir é arriscado. Em vez disso, avisa no terminal que ele não corresponde à execução, e o código de saída diferente de 0 também sinaliza a falha. É uma interpretação da regra do enunciado, e vale registrar.
- **Não capturar `Exception` genérica:** erros inesperados são bugs e devem aparecer.
- **Limitação:** partes do texto padrão do `argparse` ficam em inglês (`usage`, `error`, `the following arguments are required`). Traduzir exigiria código extra, e o conteúdo continua compreensível.

## Pergunta para conferir o entendimento

Um CSV tem 10 pedidos e **todos** são inválidos. Qual é o código de saída do programa: 0 ou 1? E se o CSV tiver uma linha com um campo a menos que o cabeçalho?

**Resposta:**
- **Todos os 10 inválidos → código 0.** Pedido inválido é um resultado normal da conferência. O programa fez o trabalho dele (leu, validou e gravou o relatório), então terminou com sucesso. O relatório vai mostrar `registros_validos: 0`, `registros_invalidos: 10` e `total_aprovado: "0.00"`. O enunciado diz isso explicitamente: código 0 "mesmo que existam pedidos inválidos".
- **Linha com um campo a menos → código 1.** Isso não é um erro de *pedido*, é um erro de *estrutura do arquivo*. O `ler_pedidos` lança `ErroEstrutural`, o `main` captura, mostra `Erro: linha N: esperados 6 campos, encontrados 5` e devolve 1. Nenhum relatório é gravado.
- **Como lembrar:** erro de **negócio** (dados de um pedido) não interrompe nada e o código é 0. Erro de **estrutura** (o arquivo em si) para tudo e o código é diferente de 0.

**Decisão confirmada pelo Vitor:** em caso de falha, o relatório antigo **não** é apagado; o programa só avisa que ele não corresponde à execução.
