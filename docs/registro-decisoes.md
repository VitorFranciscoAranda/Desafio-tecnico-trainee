# Registro de decisões, dificuldades e aprendizado

## Decisões relevantes

| Decisão | Motivo |
|---|---|
| Apenas biblioteca padrão e `unittest` | Nada para instalar, e o projeto roda em qualquer Python 3.11+ sem internet. |
| Separar leitura, validação, relatório e coordenação em módulos | Cada módulo tem uma responsabilidade. Uma mudança de regra fica em um lugar só (ex.: regra do e-mail só em `validacao.py`). |
| Exceções próprias (`ErroEstrutural`, `ErroGravacao`) | Separam "o arquivo não pode ser processado" (para tudo) de "este pedido é inválido" (continua). O coordenador só precisa capturar dois tipos de erro e mostrar a mensagem sem traceback. |
| Funções de validação devolvem a mensagem de erro em vez de lançar exceção | Permite acumular todos os erros independentes de uma linha. |
| Expressão regular antes de `Decimal` e de `date.fromisoformat` | `Decimal` aceita `1e3`, `NaN` e `-5`, e `fromisoformat` aceita `20261030`. O enunciado proíbe esses formatos. Usei `[0-9]` em vez de `\d`, que aceitaria dígitos de outros alfabetos. |
| Duplicidade em duas passadas (contar com `Counter`, depois marcar) | É a forma mais simples de invalidar também a primeira ocorrência. Feita depois da normalização, para que espaços não escondam um ID repetido. IDs vazios ficam fora da contagem. |
| Leitura com `utf-8-sig` e `csv.reader(strict=True)` | Aceita o BOM que o Excel grava, e o `strict` faz o módulo `csv` recusar CSV malformado em vez de aceitá-lo em silêncio. |
| Número da linha com `leitor.line_num` | Mantém a numeração física do arquivo mesmo com linhas em branco puladas. |
| Gravar em arquivo `.tmp` e renomear no final | Um erro no meio da gravação nunca deixa um relatório parcial com o nome definitivo. |
| `samefile` para detectar entrada igual à saída | Cobre caminhos diferentes para o mesmo arquivo (relativo, `..`, maiúsculas no Windows). |
| Relatório anterior não é apagado em caso de falha | Apagar arquivos do usuário sem pedir é arriscado. O programa avisa que o arquivo existente não corresponde à execução, e o código de saída diferente de 0 sinaliza a falha. É a minha interpretação da regra "um relatório anterior não deve ser apresentado como resultado da execução que falhou". |
| Códigos de saída 0, 1 e 2 | 0 = relatório gravado (mesmo com inválidos); 1 = falha de processamento; 2 = argumentos inválidos (padrão do `argparse`). |
| Nomes de coluna comparados exatamente, sem remover espaços | O enunciado diz "nomes exatos". ` email` (com espaço) é tratado como coluna ausente. |

## Uma dificuldade concreta

**Problema:** ao executar o projeto pelo botão de executar (F5) do editor, com o arquivo `app/__main__.py` aberto, apareceu `ModuleNotFoundError: No module named 'app'`, embora os testes passassem e o comando funcionasse para o assistente.

**Hipóteses:**
1. Faltava algum arquivo no pacote, como o `__init__.py`. Descartada: o arquivo existia, e `python -m unittest` importava `app` normalmente.
2. O Python usado pelo editor era outro. Descartada: era o mesmo 3.12.10.
3. O editor executava o arquivo como **script** (`python app\__main__.py`), e não como **módulo** (`python -m app`).

**Tentativas e conclusão:** a hipótese 3 se confirmou. Executado como script, o Python coloca a pasta `app\` no caminho de busca de módulos, e não a raiz do projeto, por isso `from app.leitura import ...` falha. Rodando `python -m app ...` a partir da raiz do projeto, funcionou. Criei também uma configuração local do editor (`.vscode/launch.json`, fora do repositório) que executa com `-m`, e o README avisa sobre isso.

## O que precisei aprender

- Diferença entre executar um script e um pacote com `python -m`.
- Por que `float` não serve para dinheiro e como `Decimal` resolve, incluindo `quantize`.
- Expressões regulares (`fullmatch`, grupos opcionais, `[0-9]` x `\d`).
- `csv.reader`, `line_num`, BOM e codificações (UTF-8 x Latin-1).
- `argparse`, códigos de saída e `stdout` x `stderr`.
- `unittest`: `assertRaises`, `subTest`, pastas temporárias, `subprocess` para testar o comando real.
- Teste de mutação: estragar o código de propósito para provar que os testes detectam erros.

## Estimativa de tempo

Referência: o desenvolvimento aconteceu em 2026-11-04, em sessões com intervalos, ao longo do dia.

## O que faria em seguida

- Traduzir as mensagens do `argparse`.
- Medir cobertura com `coverage.py` e rodar os testes em Linux e Windows com integração contínua.
- Processar arquivos grandes linha a linha, mantendo a detecção de duplicados.
- Rever com a equipe a decisão sobre o relatório anterior (apagar, renomear ou só avisar).

## Ferramentas de IA utilizadas

Usei o **Claude (Anthropic)** como assistente durante todo o desenvolvimento, em sessões guiadas. Combinei com ele que trabalharia em etapas, que cada etapa só começaria com a minha confirmação, que ele explicaria o código linha por linha e que me faria uma pergunta de verificação ao final de cada uma.

**Em que atividades ajudou:**
- Análise do enunciado e plano em 8 etapas.
- Escrita do código e dos testes, etapa por etapa, com explicações (as anotações estão em `docs/Etapas/`).
- Diagnóstico do `ModuleNotFoundError` descrito acima.
- Montagem do CSV de demonstração e revisão da matriz de testes.

**Como conferi as sugestões:**
- **Uma sugestão corrigida por informação mais completa:** o primeiro plano foi montado a partir de um resumo do desafio que eu tinha escrito, que estava incompleto. Quando enviei o documento original, a IA apontou regras que o plano não cobria (ordem livre de colunas, cabeçalho duplicado, formato restrito do valor, códigos de saída, proibição de relatório parcial), e o plano foi ajustado antes da implementação.
- **Uma sugestão conferida com testes:** a IA afirmou que `Decimal("1e3")` e `date.fromisoformat("20261030")` são aceitos pelo Python e que, por isso, era preciso validar o formato com expressão regular antes. A afirmação está coberta por testes que passam (`test_valores_invalidos` e `test_formato_errado_e_rejeitado`). ✏️ *Se quiser, confira você mesmo no terminal com `python -c "from decimal import Decimal; print(Decimal('1e3'))"`, que imprime `1E+3` em vez de dar erro.*
- **Uma decisão que eu precisei aprovar:** a IA propôs não apagar o relatório anterior quando a execução falha, só avisar. Avaliei a alternativa de apagar e confirmei a proposta, registrada acima.
- **Verificação dos próprios testes:** pedi que as regras fossem quebradas de propósito numa cópia do código (teste de mutação), para confirmar que os testes falham quando deveriam. Os resultados estão em `docs/matriz-testes.md`.
- Em cada etapa, respondi às perguntas de verificação e conferi a execução no meu terminal (por exemplo, os valores `150.50` e `1200.30` dos relatórios).
