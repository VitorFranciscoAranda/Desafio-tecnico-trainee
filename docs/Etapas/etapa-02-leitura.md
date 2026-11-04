# Etapa 2: leitura do CSV

A etapa 2 está dividida em dois pedaços pequenos:

- **2a (este):** conferir o cabeçalho do arquivo.
- **2b (próximo):** abrir o arquivo de verdade e ler as linhas.

---

## Pedaço 2a: conferir o cabeçalho

### O que e por quê

O cabeçalho é a primeira linha do CSV, com os nomes das colunas. Se ele estiver errado, não adianta validar nenhum pedido: o programa nem saberia onde está o e-mail. Por isso o enunciado chama isso de **erro estrutural**, que para tudo.

Regras do enunciado para o cabeçalho:
- as 6 colunas obrigatórias precisam existir;
- o nome é exato, e maiúsculas contam (`Email` não é `email`);
- a ordem pode variar, e colunas a mais são ignoradas;
- coluna repetida é erro.

Separei essa conferência numa função própria, que recebe uma **lista de nomes** em vez de um arquivo. Assim ela fica fácil de testar: basta passar uma lista, sem criar arquivos.

### O código (`app/leitura.py`)

```python
COLUNAS_OBRIGATORIAS = ("pedido_id", "cliente", "email", "valor", "data_pedido", "status")
```
- Uma **tupla** com os nomes obrigatórios. Usei tupla, e não lista, porque ela não pode ser alterada: é uma constante.
- O nome em MAIÚSCULAS é a convenção do Python para "isto é uma constante".

```python
class ErroEstrutural(Exception):
    """Problema no arquivo que impede o processamento (ex.: coluna ausente)."""
```
- Uma **exceção própria**. Herdando de `Exception`, ela funciona como qualquer erro do Python e pode ser usada com `raise` e `except`.
- Por que criar uma? Para separar dois tipos de problema:
  - **erro estrutural** (o arquivo está quebrado): para tudo;
  - **erro de negócio** (um pedido com e-mail ruim): só aquele pedido fica inválido.
- Na etapa 5, o programa principal vai fazer `except ErroEstrutural` para mostrar a mensagem e sair com código diferente de 0.
- A classe não tem corpo além da docstring, e isso basta: herdar de `Exception` já dá tudo o que ela precisa.

```python
def validar_cabecalho(cabecalho):
```
- Recebe `cabecalho`, uma lista como `["pedido_id", "cliente", ...]`.
- Não devolve nada quando está tudo certo. Quando há problema, **lança** uma exceção.

```python
    duplicadas = sorted({nome for nome in cabecalho if cabecalho.count(nome) > 1})
```
Lendo de dentro para fora:
- `cabecalho.count(nome)` conta quantas vezes o nome aparece na lista.
- `{nome for nome in cabecalho if ...}` é uma **compreensão de conjunto (set)**: percorre a lista e guarda os nomes que aparecem mais de uma vez. Usei conjunto para que `email` repetido apareça uma vez só na mensagem.
- `sorted(...)` transforma o conjunto em lista ordenada, para a mensagem sair sempre igual.

```python
    if duplicadas:
        raise ErroEstrutural(f"cabeçalho com colunas duplicadas: {', '.join(duplicadas)}")
```
- `if duplicadas:` uma lista vazia vale como `False` e uma lista com itens vale como `True`.
- `raise` interrompe a função e "lança" o erro para quem a chamou.
- `', '.join(lista)` junta os itens com vírgula: `["a", "b"]` vira `"a, b"`.

```python
    ausentes = [nome for nome in COLUNAS_OBRIGATORIAS if nome not in cabecalho]
    if ausentes:
        raise ErroEstrutural(f"coluna obrigatória ausente: {', '.join(ausentes)}")
```
- **Compreensão de lista**: para cada nome obrigatório, guarda os que **não** estão no cabeçalho.
- Se sobrou algum, lança o erro dizendo quais faltam.
- Repare que nada aqui olha a posição das colunas. Por isso a ordem pode variar, e colunas extras não atrapalham.

### Os testes (`tests/test_leitura.py`)

| Teste | O que confere |
|---|---|
| `test_aceita_ordem_diferente_e_coluna_extra` | Colunas embaralhadas e uma coluna `observacao` a mais: não dá erro. |
| `test_coluna_obrigatoria_ausente` | Sem `email`: lança `ErroEstrutural` e a mensagem cita `email`. |
| `test_coluna_duplicada` | `email` duas vezes: lança erro com a palavra "duplicadas". |
| `test_nome_de_coluna_diferencia_maiusculas` | `Pedido_ID` não vale como `pedido_id`. |

`with self.assertRaises(ErroEstrutural) as contexto:` significa "o código dentro deste bloco **tem que** lançar esse erro". Se não lançar, o teste falha. Depois, `str(contexto.exception)` pega o texto da mensagem para conferir.

### Execução

```
> python -m unittest discover -v
... 6 testes ...
Ran 6 tests in 0.000s
OK
```

Exemplo do erro, chamando a função direto com o e-mail faltando:
```
app.leitura.ErroEstrutural: coluna obrigatória ausente: email
```

### Decisão para anotar no registro

Os nomes de coluna são comparados **exatamente**, sem remover espaços, porque o enunciado diz "nomes exatos". Um cabeçalho com ` email` (com espaço antes) é tratado como coluna ausente.

### Pergunta para conferir o entendimento

Se o cabeçalho vier sem `email` **e** com `status` repetido, qual das duas mensagens aparece? Por quê?

**Resposta:** aparece `cabeçalho com colunas duplicadas: status`. As duplicadas são conferidas primeiro, e o `raise` interrompe a função na hora, então a checagem de ausentes nem chega a rodar. Para erros estruturais isso basta. Na etapa 3, os pedidos vão fazer o contrário: juntar todos os erros numa lista.

---

## Pedaço 2b: abrir o arquivo e ler as linhas

### O que e por quê

Agora a função `ler_pedidos(caminho)` abre o arquivo de verdade e devolve uma **lista de registros**. Cada registro é um dicionário assim:

```python
{'pedido_id': 'PED-001', 'cliente': 'Alfa', 'email': 'a@alfa.com',
 'valor': '150.50', 'data_pedido': '2026-10-29', 'status': 'APROVADO', 'linha': 2}
```

Ela cuida só da **estrutura** do arquivo. Ela **não** confere se o e-mail é bom ou se o valor é positivo: isso é trabalho da etapa 3. Os valores saem exatamente como estão no arquivo, ainda com espaços. Separar assim deixa cada parte pequena e fácil de testar.

O que ela precisa fazer, segundo o enunciado:
- erro se o arquivo não existe, está vazio, não é UTF-8 ou é um CSV malformado;
- conferir o cabeçalho (com a função do 2a);
- pular linhas totalmente em branco;
- manter linhas como `,,,,,` (elas viram registros inválidos na etapa 3);
- erro se uma linha tiver mais ou menos campos que o cabeçalho;
- guardar o **número da linha física**, porque o relatório precisa dele.

### O código, parte por parte

```python
import csv
from pathlib import Path
```
- `csv`: módulo nativo que entende o formato CSV, inclusive campos entre aspas como `"Silva, Ana"`. Dividir a linha com `split(",")` quebraria esse nome em dois.
- `Path`: representa um caminho de arquivo. Tem métodos práticos como `is_file()` e `open()`, e funciona igual no Windows e no Linux.

```python
def linha_em_branco(campos):
    return len(campos) <= 1 and "".join(campos).strip() == ""
```
- O `csv.reader` transforma cada linha numa lista de textos (`campos`).
- Linha vazia vira `[]`. Linha só com espaços vira `["   "]`. Nos dois casos não há nenhuma vírgula, então a lista tem 0 ou 1 item.
- `",,,,,"` vira `["", "", "", "", "", ""]`, com 6 itens. Essa **não** é "em branco": tem separadores, e por isso é mantida, como pede o enunciado.
- `"".join(campos).strip() == ""` confere se, juntando tudo e tirando os espaços, não sobra nada.

```python
    caminho = Path(caminho)
    if not caminho.is_file():
        raise ErroEstrutural(f"arquivo de entrada não encontrado: {caminho}")
```
- Aceita tanto texto quanto `Path` e converte para `Path`.
- `is_file()` é falso se o arquivo não existe **ou** se o caminho é uma pasta. Assim a mensagem já sai clara logo no começo.

```python
    registros = []
    try:
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
```
- `try:` começa um bloco em que os erros serão "capturados" mais abaixo, nos `except`.
- `with ... as arquivo:` abre o arquivo e **garante que ele seja fechado** no final, mesmo se der erro no meio. É a forma recomendada de abrir arquivos em Python.
- `encoding="utf-8-sig"`: lê como UTF-8 e ignora o BOM. O BOM é uma "marca invisível" de 3 bytes que o Excel coloca no começo de arquivos UTF-8. Sem o `-sig`, o primeiro nome de coluna viria como `"\ufeffpedido_id"` e daria "coluna ausente".
- `newline=""`: recomendação da documentação do `csv`. Deixa o próprio módulo cuidar das quebras de linha (`\r\n` no Windows, `\n` no Linux).
- Abrimos só para **leitura** (o modo padrão é `"r"`). O arquivo de entrada nunca é modificado.

```python
            leitor = csv.reader(arquivo, strict=True)
```
- Cria o leitor de CSV. `strict=True` faz o leitor reclamar de CSV malformado, como `"Alfa"x` (texto depois de fechar as aspas), em vez de "adivinhar" o que o arquivo quis dizer.

```python
            cabecalho = next(leitor, None)
            if cabecalho is None:
                raise ErroEstrutural("arquivo vazio: o cabeçalho é obrigatório")
            validar_cabecalho(cabecalho)
```
- `next(leitor, None)` pega a **primeira** linha. Se o arquivo não tiver nenhuma linha, devolve `None` em vez de dar erro.
- Arquivo vazio é erro estrutural. Arquivo **só com cabeçalho** passa daqui e devolve uma lista vazia, que é o comportamento pedido.
- Depois, reaproveita a função do 2a.

```python
            for campos in leitor:
                if linha_em_branco(campos):
                    continue
```
- O `for` continua do ponto onde o `next` parou, ou seja, a partir da linha 2.
- `continue` pula para a próxima volta do laço, ignorando a linha em branco.

```python
                if len(campos) != len(cabecalho):
                    raise ErroEstrutural(
                        f"linha {leitor.line_num}: esperados {len(cabecalho)} campos, "
                        f"encontrados {len(campos)}"
                    )
```
- Se a linha tem mais ou menos campos que o cabeçalho, é erro estrutural e o processamento para.
- `leitor.line_num` é o número da linha que o leitor acabou de ler, contando a partir de 1. Como o enunciado garante que nenhum campo tem quebra de linha dentro, ele é igual à **linha física** do arquivo, contando as linhas em branco puladas.
- Duas f-strings lado a lado dentro dos parênteses são juntadas automaticamente. Isso só serve para a linha não ficar comprida demais.

```python
                registro = {nome: campos[cabecalho.index(nome)] for nome in COLUNAS_OBRIGATORIAS}
                registro["linha"] = leitor.line_num
                registros.append(registro)
```
- **Compreensão de dicionário**: para cada coluna obrigatória, descobre a posição dela no cabeçalho (`cabecalho.index(nome)`) e pega o valor dessa posição na linha.
- É isso que permite **qualquer ordem** de colunas: buscamos pelo nome, não pela posição fixa.
- Colunas extras nunca entram no dicionário, porque só percorremos as obrigatórias.
- Por fim, guarda o número da linha e adiciona o registro à lista.

```python
    except UnicodeDecodeError:
        raise ErroEstrutural("o arquivo de entrada não está codificado em UTF-8")
    except csv.Error as erro:
        raise ErroEstrutural(f"CSV malformado na linha {leitor.line_num}: {erro}")
    except OSError as erro:
        raise ErroEstrutural(f"não foi possível ler o arquivo de entrada: {erro}")
```
- Cada `except` captura um tipo de erro que o Python lança e o **traduz** para um `ErroEstrutural` com mensagem em português.
- `UnicodeDecodeError`: o arquivo tem bytes que não são UTF-8 válido, como um arquivo salvo em "ANSI/Latin-1" no Bloco de Notas antigo.
- `csv.Error`: o leitor encontrou um CSV malformado (por causa do `strict=True`).
- `OSError`: outros problemas do sistema, como falta de permissão para ler.
- Vantagem: o programa principal (etapa 5) só precisa capturar **um** tipo de erro, `ErroEstrutural`, mostrar a mensagem e sair com código diferente de 0, sem traceback.

```python
    return registros
```
- Só chega aqui se o arquivo inteiro foi lido sem erro estrutural. Ou seja, **nunca** devolvemos um resultado pela metade.

### Os testes novos (`TestLerPedidos`)

Cada teste cria um CSV numa **pasta temporária** (`tempfile.TemporaryDirectory`), que é apagada no final. Assim os testes não sujam a pasta `dados/`.
- `setUp` roda antes de **cada** teste e cria a pasta.
- `addCleanup` agenda a limpeza para depois do teste, mesmo se ele falhar.
- `criar_csv` grava **bytes** (`write_bytes`). Isso dá controle total, por exemplo para gravar em Latin-1 de propósito.

| Teste | O que confere |
|---|---|
| `test_le_registros_com_numero_da_linha` | Lê 2 pedidos; a linha em branco é pulada e o segundo fica com `linha` 4. |
| `test_ordem_diferente_e_coluna_extra` | Colunas embaralhadas são lidas certo e a coluna extra `obs` fica de fora. |
| `test_campo_entre_aspas_com_virgula` | `"Silva, Ana"` vira um campo só. |
| `test_linha_so_com_separadores_vira_registro` | `,,,,,` vira um registro com campos vazios. |
| `test_linha_com_espacos_e_ignorada` | Linha só com espaços é tratada como em branco. |
| `test_somente_cabecalho_tem_zero_registros` | Só cabeçalho devolve `[]` (parte do T06). |
| `test_aceita_bom_do_excel` | Arquivo com BOM é lido normalmente. |
| `test_arquivo_vazio` | 0 bytes gera erro "vazio". |
| `test_arquivo_inexistente` | Gera erro "não encontrado" (parte do T07). |
| `test_quantidade_de_campos_diferente` | Linha com 5 campos gera erro citando "linha 2". |
| `test_codificacao_invalida` | `João` gravado em Latin-1 gera erro "UTF-8" (será o nosso T09). |
| `test_csv_malformado` | `"Alfa"x` gera erro "malformado". |

### Execução

```
> python -m unittest discover
..................
Ran 18 tests in 0.065s
OK
```

Exemplo com um arquivo que tem um pedido, uma linha em branco (linha 3) e uma linha ` ,,,,,` (linha 4):
```
{'pedido_id': 'PED-001', 'cliente': 'Alfa', ..., 'status': 'APROVADO', 'linha': 2}
{'pedido_id': ' ', 'cliente': '', 'email': '', 'valor': '', 'data_pedido': '', 'status': '', 'linha': 4}
ErroEstrutural: arquivo de entrada não encontrado: nao_existe.csv
```
Repare que o `pedido_id` da linha 4 ainda tem o espaço `' '`: a limpeza dos espaços fica para a etapa 3.

### Decisões para anotar no registro

- **`utf-8-sig` em vez de `utf-8`:** aceita arquivos salvos pelo Excel com BOM, que de outra forma dariam "coluna ausente" por causa de um caractere invisível.
- **`strict=True`:** o enunciado diz que CSV malformado é erro estrutural; sem isso, o módulo `csv` aceitaria alguns erros em silêncio.
- **Linha só com espaços = em branco:** ela não tem separadores nem conteúdo, então foi tratada como "totalmente em branco".
- **Leitura separada da validação:** `ler_pedidos` não remove espaços nem confere regras de negócio. Isso fica todo na etapa 3.

### Pergunta para conferir o entendimento

Um arquivo tem o cabeçalho na linha 1, duas linhas em branco (2 e 3) e um pedido na linha 4. Qual número aparece em `registro["linha"]` para esse pedido? E por que é importante não usar simplesmente "posição na lista + 2"?

**Resposta:** aparece **4**. O `leitor.line_num` conta todas as linhas lidas, inclusive as em branco que foram puladas. O pedido é o primeiro da lista (posição 0), mas "posição + 2" daria 2, e quem abrisse o CSV para corrigir procuraria na linha errada. Pular linha em branco não torna nenhum registro inválido.
