# Plano do projeto e Etapa 1: ambiente e estrutura inicial

## 1. O que encontrei na pasta

- A pasta `C:\Users\Adm\Desktop\Desafio` **não era um clone** do GitHub. Tinha só três pastas vazias: `App`, `Entradas` e `Saidas`.
- Não consegui ler o repositório `VitorFranciscoAranda/Desafio-tecnico-trainee` sem login (ele é privado ou ainda não existe). Então rodei `git init` na pasta e cadastrei esse endereço como `origin`. **Nenhum commit nem push foi feito.**
- Renomeei as pastas para os nomes pedidos no desafio:
  - `App` → `app` (precisa ser minúsculo: o Python no Windows diferencia maiúsculas no `import`, então `python -m app` falharia com `App`).
  - `Entradas` → `dados` e `Saidas` → `saida`.
- Python instalado: **3.12.10** (atende ao requisito 3.11+). Git 2.52.

## 2. Estrutura proposta

```
Desafio/
├── app/                  pacote da aplicação
│   ├── __init__.py       marca a pasta como pacote; guarda a versão
│   ├── __main__.py       ponto de entrada de "python -m app" (CLI com argparse)
│   ├── leitura.py        lê o CSV e verifica a estrutura
│   ├── validacao.py      regras de validação de cada pedido
│   └── relatorio.py      monta e grava o JSON
├── tests/                testes automatizados (unittest)
├── dados/                CSVs de exemplo e de demonstração
├── saida/                relatórios JSON gerados
├── docs/                 explicações de cada etapa (para estudo)
├── .gitignore
└── README.md
```

Por que separar assim: cada módulo tem **uma responsabilidade**. Se a regra do e-mail mudar, só mexo em `validacao.py`. Se o formato do relatório mudar, só em `relatorio.py`. Isso também facilita testar cada parte isoladamente.

## 3. Plano em etapas

| Etapa | Entrega | O que se aprende |
|---|---|---|
| 1 | Ambiente e estrutura (esta) | pacotes, `python -m`, `unittest`, git |
| 2 | `leitura.py` | `csv.DictReader`, codificação UTF-8, exceções próprias, linhas em branco |
| 3 | `validacao.py` | `strip`, `Decimal`, `datetime.date.fromisoformat`, acúmulo de erros, IDs duplicados com `Counter` |
| 4 | `relatorio.py` | `json.dump`, soma com `Decimal`, `quantize` para 2 casas |
| 5 | CLI em `__main__.py` | `argparse`, `--help`, `pathlib`, criar pasta de saída, impedir entrada = saída, códigos de saída |
| 6 | Testes completos (10 cenários) | `unittest`, arquivos temporários, `subprocess` para testar o terminal |
| 7 | Dados de demonstração e relatório | CSV com 12+ registros cobrindo todos os casos |
| 8 | README e registro de decisões | documentação |

Cada etapa já vem com seus próprios testes. A etapa 6 fecha os 10 cenários exigidos.

**Testes:** vou usar `unittest`, que já vem com o Python. Assim não é preciso instalar nada (nem `pip install`), o que cumpre "preferencialmente bibliotecas nativas". Comando único: `python -m unittest discover -v`.

**Ambiente virtual (`.venv`):** como não há dependências externas, ele não é obrigatório. Ele serve para isolar bibliotecas de um projeto das de outro. Deixei `.venv/` no `.gitignore` caso você queira criar um (`python -m venv .venv`).

## 4. Arquivos criados nesta etapa

### `app/__init__.py`

```python
"""Sistema de Conferência de Pedidos. ..."""
__version__ = "0.1.0"
```

- A existência de `__init__.py` faz a pasta `app` ser um **pacote**: é o que permite `from app import ...`.
- O texto entre `"""` é uma *docstring*: documentação que o Python guarda junto com o módulo.
- `__version__` é uma convenção para guardar a versão do pacote. Usamos no `__main__.py`.

### `app/__main__.py`

```python
import sys
from app import __version__

def main() -> int:
    print(f"Sistema de Conferência de Pedidos v{__version__}")
    print(f"Python {sys.version.split()[0]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Linha por linha:

- `import sys`: módulo nativo com informações do interpretador (versão, argumentos, saída).
- `from app import __version__`: importa a variável definida no `__init__.py`.
- `def main() -> int:` define a função principal. `-> int` é uma *type hint*: avisa que a função devolve um inteiro. Não muda a execução, só documenta.
- `print(f"...")`: *f-string*, permite colocar variáveis dentro de `{}`.
- `sys.version.split()[0]`: `sys.version` é algo como `"3.12.10 (tags/...)"`. O `split()` quebra nos espaços e `[0]` pega só `"3.12.10"`.
- `return 0`: por convenção, 0 significa "sucesso" para o sistema operacional. Depois vamos devolver outros números para erros.
- `if __name__ == "__main__":` só é verdadeiro quando o arquivo é **executado**, não quando é **importado** (como no teste). Isso evita que o programa rode sozinho ao ser importado.
- `sys.exit(main())`: encerra o programa devolvendo o código de `main()`.

**Por que `__main__.py`?** Quando você roda `python -m app`, o Python procura `app/__main__.py` e o executa. É exatamente o formato de comando que o desafio pede.

### `tests/__init__.py` (vazio) e `tests/test_ambiente.py`

```python
import sys, unittest
from app.__main__ import main

class TestAmbiente(unittest.TestCase):
    def test_versao_do_python(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))

    def test_main_retorna_zero(self):
        self.assertEqual(main(), 0)
```

- Uma classe que herda de `unittest.TestCase` agrupa testes.
- Todo método que começa com `test_` é encontrado e executado automaticamente.
- `sys.version_info[:2]` é a tupla `(3, 12)`. Tuplas são comparadas elemento por elemento, então `(3, 12) >= (3, 11)` é verdadeiro.
- `assertEqual` e `assertGreaterEqual` são as **verificações explícitas**: se o valor não for o esperado, o teste falha e mostra a diferença.
- `tests/__init__.py` vazio transforma `tests` em pacote, o que o `discover` precisa para importar os testes.

### Outros

- `.gitignore`: lista o que o git não deve versionar (cache `__pycache__`, `.venv`, configurações do Visual Studio).
- `dados/.gitkeep` e `saida/.gitkeep`: o git não guarda pastas vazias. Esse arquivo vazio garante que as pastas existam no repositório.
- `README.md`: esqueleto, completado na etapa 8.

## 5. Execução e verificação

```
> python -m app
Sistema de Conferência de Pedidos v0.1.0
Python 3.12.10

> python -m unittest discover -v
test_main_retorna_zero (tests.test_ambiente.TestAmbiente.test_main_retorna_zero) ... ok
test_versao_do_python (tests.test_ambiente.TestAmbiente.test_versao_do_python) ... ok
Ran 2 tests in 0.000s
OK
```

Os dois comandos funcionaram: o pacote é executável e os testes rodam com um único comando.

## 6. Pergunta de entrevista que pode aparecer

> "Por que `python -m app` e não `python app/__main__.py`?"

Com `-m`, o Python executa `app` como pacote, a partir da raiz do projeto. Assim os imports `from app import ...` funcionam igual no programa e nos testes.

## 7. Antes da etapa 2, preciso de uma coisa

O desafio pede "um CSV de exemplo com os três pedidos apresentados no desafio", mas esses três pedidos não estão no texto que recebi. Se puder, cole aqui o cabeçalho e as três linhas do enunciado original.
