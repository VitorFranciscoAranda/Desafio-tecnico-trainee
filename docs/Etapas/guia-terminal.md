# Guia: como executar o projeto pelo terminal

Este guia usa o terminal que fica dentro do editor (VS Code), que no Windows abre o **PowerShell**.

## 1. Abrir a pasta certa no editor

Menu **Arquivo → Abrir Pasta...** e escolha `C:\Users\Adm\Desktop\Desafio`. Na barra lateral devem aparecer `app`, `dados`, `docs`, `saida` e `tests`.

## 2. Abrir o terminal

Menu **Terminal → Novo Terminal**, ou o atalho **Ctrl + '** (a tecla de aspas simples, ao lado do Enter).

Abre um painel embaixo com uma linha parecida com esta:

```
PS C:\Users\Adm\Desktop\Desafio>
```

Essa linha é o **prompt**. Ela mostra em qual pasta o terminal está agora. Tudo o que você digitar será executado **a partir dessa pasta**.

## 3. Conferir se está na pasta certa

O prompt precisa terminar em `Desafio>`. Se não terminar, digite e aperte Enter:

```
cd C:\Users\Adm\Desktop\Desafio
```

- `cd` significa *change directory*, ou seja, "mudar de pasta".

Para conferir, liste o que tem na pasta:

```
ls
```

Devem aparecer `app`, `dados`, `docs`, `saida`, `tests` e `README.md`.

**Por que isso importa?** O `python -m app` procura a pasta `app` **dentro da pasta atual**. Se o terminal estiver em outra pasta, aparece o mesmo `No module named 'app'` de antes.

## 4. Conferir o Python

```
python --version
```

Deve aparecer `Python 3.12.10`. O projeto precisa de 3.11 ou mais novo.

## 5. Rodar o programa

```
python -m app --entrada dados/pedidos.csv --saida saida/relatorio.json --data-referencia 2026-10-30
```

O comando é uma linha só. Cada pedaço significa:

| Pedaço | Significado |
|---|---|
| `python` | chama o Python |
| `-m app` | executa o **pacote** `app` (o Python roda o `app/__main__.py`) |
| `--entrada dados/pedidos.csv` | qual CSV ler |
| `--saida saida/relatorio.json` | onde gravar o relatório |
| `--data-referencia 2026-10-30` | a data usada para recusar pedidos futuros (opcional) |

Os caminhos são **relativos** à pasta atual: `dados/pedidos.csv` quer dizer "a pasta `dados` que está aqui dentro". No Windows, tanto faz usar `/` ou `\`.

Resultado esperado:

```
Conferência concluída.
  Data de referência:   2026-10-30
  Total de registros:   3
  Registros válidos:    2
  Registros inválidos:  1
  Total aprovado:       150.50
  Relatório gravado em: saida\relatorio.json
```

## 6. Ver o resultado

Mostrar o relatório no terminal:

```
Get-Content saida/relatorio.json
```

(`cat saida/relatorio.json` também funciona no PowerShell.) Também dá para abrir o arquivo pela barra lateral do editor, na pasta `saida`.

Ver o **código de saída** da última execução:

```
$LASTEXITCODE
```

Deve mostrar `0`. Se você rodar com um arquivo que não existe, deve mostrar `1`:

```
python -m app --entrada nao_existe.csv --saida saida/relatorio.json
$LASTEXITCODE
```

## 7. Rodar os testes

```
python -m unittest discover -v
```

- `-m unittest` chama o módulo de testes do Python.
- `discover` procura sozinho todos os arquivos `test_*.py` da pasta `tests`.
- `-v` (*verbose*) mostra o nome de cada teste. Sem ele, aparece só um ponto por teste.

No final deve aparecer `OK`. Se algum teste falhar, aparece `FAILED` com o nome do teste e a diferença entre o esperado e o obtido.

## 8. Atalhos úteis

- **Seta para cima (↑):** traz de volta o último comando, sem precisar digitar de novo.
- **Tab:** completa nomes de pastas e arquivos. Digite `dados/pe` e aperte Tab.
- **Ctrl + C:** interrompe um comando que está rodando.
- **`python -m app --help`:** mostra a ajuda do programa com todos os argumentos.
- **`cls`:** limpa a tela do terminal.
