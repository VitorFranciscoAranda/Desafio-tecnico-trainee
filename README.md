# Sistema de Conferência de Pedidos

**Autor:** Vitor Aranda. Desafio técnico do processo seletivo para trainee em engenharia de software e qualidade.

Aplicação de linha de comando em Python que lê pedidos de um arquivo CSV, valida cada registro, identifica inconsistências e gera um relatório JSON com as contagens, o total aprovado e a lista de registros inválidos com seus erros.

## Visão geral

1. **Leitura** (`app/leitura.py`): abre o CSV em UTF-8, confere o cabeçalho e a estrutura e devolve os registros com o número da linha original. Problemas de estrutura interrompem a execução.
2. **Validação** (`app/validacao.py`): remove espaços externos, normaliza o status, confere cada campo, acumula todos os erros de cada registro e detecta IDs duplicados.
3. **Relatório** (`app/relatorio.py`): soma com `Decimal` os valores dos pedidos válidos com status APROVADO, monta o JSON e o grava sem deixar arquivo parcial.
4. **Coordenação** (`app/__main__.py`): lê os argumentos, chama as etapas acima, mostra o resumo no terminal e devolve o código de saída.

## Pré-requisitos

- **Python 3.11 ou superior.** Desenvolvido e testado com **Python 3.12.10** no Windows 11.
- **Nenhuma dependência externa.** O projeto usa apenas a biblioteca padrão do Python (`argparse`, `csv`, `json`, `decimal`, `datetime`, `re`, `pathlib`, `collections`, `unittest`). O arquivo `requirements.txt` existe só para registrar isso e não lista pacotes.
- Não precisa de internet, credenciais ou serviços pagos.

## Instalação

A partir de uma pasta recém-clonada ou extraída do ZIP:

```bash
git clone https://github.com/VitorFranciscoAranda/Desafio-tecnico-trainee.git
cd Desafio-tecnico-trainee
python --version
```

Confirme que a versão é 3.11 ou maior. No Windows, se `python` não for reconhecido, use `py`.

O ambiente virtual é **opcional**, porque não há pacotes para instalar. Se quiser isolar o projeto mesmo assim:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

No Linux ou macOS, ative com `source .venv/bin/activate`. O `pip install` termina sem instalar nada.

> Todos os comandos abaixo devem ser executados **na pasta raiz do projeto** (a que contém `app/`). Executar `app/__main__.py` diretamente, sem o `-m`, causa `ModuleNotFoundError: No module named 'app'`.

## Execução

**Exemplo do enunciado:**

```bash
python -m app --entrada dados/pedidos.csv --saida saida/relatorio.json --data-referencia 2026-10-30
```

```
Conferência concluída.
  Data de referência:   2026-10-30
  Total de registros:   3
  Registros válidos:    2
  Registros inválidos:  1
  Total aprovado:       150.50
  Relatório gravado em: saida\relatorio.json
```

**Conjunto de demonstração** (comando exato usado para gerar o relatório entregue):

```bash
python -m app --entrada dados/pedidos_demonstracao.csv --saida saida/relatorio_demonstracao.json --data-referencia 2026-10-30
```

Resultado: 19 registros, 6 válidos, 13 inválidos, total aprovado `1200.30`.

**Ajuda:**

```bash
python -m app --help
```

## Argumentos

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `--entrada CAMINHO` | sim | Arquivo CSV de pedidos. Nunca é modificado. |
| `--saida CAMINHO` | sim | Onde gravar o relatório JSON. A pasta é criada se não existir. Um relatório existente nesse caminho é substituído. Não pode ser o mesmo arquivo da entrada. |
| `--data-referencia AAAA-MM-DD` | não | Pedidos com data **posterior** a ela são inválidos; uma data **igual** é aceita. Precisa ser uma data real no formato exato. **Se omitido, usa a data local do computador**, obtida uma única vez no início da execução. |

## Códigos de saída

| Código | Situação |
|---|---|
| `0` | Processamento concluído e relatório gravado, **mesmo que existam pedidos inválidos**. |
| `1` | Falha de processamento: arquivo de entrada inexistente ou ilegível, erro estrutural no CSV, codificação inválida, entrada igual à saída ou falha ao gravar o relatório. |
| `2` | Argumentos inválidos: falta `--entrada` ou `--saida`, ou `--data-referencia` inválida. |

Em qualquer falha, o programa mostra uma mensagem em português, sem traceback, e não grava relatório. Se já existir um relatório anterior no caminho de saída, ele **não é apagado**, e o programa avisa que ele não corresponde à execução que falhou.

## Formato dos arquivos

### Entrada (CSV)

- UTF-8 (o BOM gravado pelo Excel é aceito), vírgula como separador, cabeçalho na primeira linha, campos podem estar entre aspas duplas.
- Colunas obrigatórias, com nome exato e sensível a maiúsculas: `pedido_id`, `cliente`, `email`, `valor`, `data_pedido`, `status`. A ordem é livre e colunas extras são ignoradas.

| Campo | Regra |
|---|---|
| `pedido_id` | Não vazio e único no arquivo. A comparação diferencia maiúsculas. Todas as ocorrências de um ID repetido são inválidas. |
| `cliente` | Não vazio. |
| `email` | Exatamente um `@`, conteúdo dos dois lados e nenhum espaço. |
| `valor` | Maior que zero; apenas dígitos, com ponto e uma ou duas casas opcionais (`10`, `10.5`, `10.50`). |
| `data_pedido` | Data existente no formato `AAAA-MM-DD`, não posterior à data de referência. |
| `status` | `PENDENTE`, `APROVADO` ou `CANCELADO`, sem diferenciar maiúsculas. |

Antes de validar, os espaços nas pontas de todos os campos são removidos e o status é convertido para maiúsculas.

**Erros estruturais** (interrompem a execução): arquivo vazio, cabeçalho duplicado, coluna obrigatória ausente, linha com quantidade de campos diferente do cabeçalho, codificação que não é UTF-8 e CSV malformado. Linhas totalmente em branco são ignoradas. Uma linha só com separadores (`,,,,,`) é um registro inválido.

### Saída (JSON)

```json
{
  "data_referencia": "2026-10-30",
  "total_registros": 3,
  "registros_validos": 2,
  "registros_invalidos": 1,
  "total_aprovado": "150.50",
  "invalidos": [
    {"linha": 4, "pedido_id": "PED-003", "erros": ["email: formato inválido"]}
  ]
}
```

- `linha` é a linha física do CSV (o cabeçalho é a linha 1).
- `total_aprovado` é uma string com duas casas, `"0.00"` quando não há valores elegíveis.
- Os inválidos seguem a ordem do arquivo. Cada mensagem começa pelo nome do campo.

## Estrutura do projeto

```
├── app/
│   ├── __init__.py          versão do pacote
│   ├── __main__.py          linha de comando e coordenação
│   ├── leitura.py           leitura e verificação estrutural do CSV
│   ├── validacao.py         normalização, regras dos campos e duplicidade
│   └── relatorio.py         soma, montagem e gravação do JSON
├── tests/                   testes automatizados (unittest)
├── dados/
│   ├── pedidos.csv                  exemplo do enunciado
│   └── pedidos_demonstracao.csv     demonstração com 19 registros
├── saida/
│   ├── relatorio.json               relatório do exemplo
│   └── relatorio_demonstracao.json  relatório da demonstração
├── docs/
│   ├── matriz-testes.md             matriz de cenários e resultados
│   ├── registro-decisoes.md         decisões, dificuldades, aprendizado e uso de IA
│   ├── evidencias/                  saída real da última execução dos testes
│   └── Etapas/                      anotações de estudo de cada etapa do desenvolvimento
├── requirements.txt
└── README.md
```

## Testes

```bash
python -m unittest discover -v
```

São **63 testes**, cobrindo os cenários obrigatórios T01 a T08 e dois escolhidos: **T09**, arquivo com codificação inválida, e **T10**, mesmo arquivo como entrada e saída. Resumo da última execução: `Ran 63 tests ... OK`.

- Matriz com cenário, resultado esperado, teste e situação: [`docs/matriz-testes.md`](docs/matriz-testes.md).
- Saída completa da última execução: [`docs/evidencias/testes-ultima-execucao.txt`](docs/evidencias/testes-ultima-execucao.txt).

Os testes criam seus arquivos em pastas temporárias e não alteram `dados/` nem `saida/`.

## Limitações conhecidas

- Textos padrão do `argparse` aparecem em inglês (`usage`, `error`, `the following arguments are required`).
- O arquivo é lido inteiro para a memória antes de validar. É suficiente para o volume do desafio, mas não para arquivos muito grandes.
- Em caso de falha, o relatório anterior não é apagado, só sinalizado no terminal (decisão explicada no registro).
- Os testes foram executados apenas no Windows. O código usa só a biblioteca padrão e `pathlib` e deve funcionar em Linux e macOS, mas isso não foi verificado.
- A falha de gravação foi testada com um destino que é uma pasta. Disco cheio e falta de permissão não foram simulados.

## Próximos passos

- Traduzir as mensagens do `argparse`.
- Medir a cobertura dos testes com `coverage.py`.
- Rodar os testes automaticamente em Linux e Windows a cada envio (integração contínua).
- Processar o arquivo em fluxo (linha a linha) para suportar arquivos grandes, mantendo a detecção de duplicados.

## Decisões e uso de IA

Ver [`docs/registro-decisoes.md`](docs/registro-decisoes.md).
