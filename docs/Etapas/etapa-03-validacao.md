# Etapa 3: validação dos pedidos

A etapa 3 está dividida em dois pedaços:

- **3a (este):** limpar os valores e conferir cada campo de um pedido.
- **3b (próximo):** encontrar IDs duplicados e juntar tudo, separando válidos de inválidos.

---

## Pedaço 3a: limpar e conferir cada campo

### O que e por quê

A etapa 2 entrega os pedidos "crus", do jeito que estão no arquivo. Agora, para cada pedido:

1. **Normalizar:** tirar os espaços das pontas de todos os campos e passar o `status` para maiúsculas.
2. **Conferir cada campo** e montar uma **lista com todos os erros** encontrados.

Lembra da pergunta do 2a? Lá, o `raise` parava no primeiro problema. Aqui é o contrário: o enunciado pede para **acumular** todos os erros de uma linha. Por isso as funções não lançam exceções. Cada uma **devolve** a mensagem de erro, ou `None` quando o campo está certo, e no final juntamos tudo numa lista.

### Recursos do Python usados

- `re` (expressões regulares): descrevem o "formato" que um texto precisa ter.
- `datetime.date`: representa uma data e sabe se ela existe (30 de fevereiro não existe).
- `decimal.Decimal`: números decimais exatos, sem os erros de arredondamento do `float`.
- `None`: o valor que significa "nada". Aqui quer dizer "sem erro".

### O código (`app/validacao.py`)

#### Constantes

```python
STATUS_PERMITIDOS = ("PENDENTE", "APROVADO", "CANCELADO")

PADRAO_VALOR = re.compile(r"[0-9]+(\.[0-9]{1,2})?")
PADRAO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
```
- `re.compile` prepara a expressão regular uma vez só, para ser reaproveitada em todos os pedidos.
- O `r` antes das aspas cria uma *raw string*: a barra `\` é tratada como texto comum, o que é importante em regex.
- Lendo o `PADRAO_VALOR` pedaço por pedaço:
  - `[0-9]+`: um ou mais dígitos de 0 a 9;
  - `\.`: um ponto de verdade (sem a barra, o `.` em regex significa "qualquer caractere");
  - `[0-9]{1,2}`: uma ou duas casas decimais;
  - `( ... )?`: o grupo com ponto e casas é **opcional**.
  - Resultado: aceita `10`, `10.5` e `10.50`. Recusa `-10`, `+10`, `10,50`, `1e3`, `NaN`, `.5`, `10.` e `10.555`.
- `PADRAO_DATA`: 4 dígitos, hífen, 2 dígitos, hífen, 2 dígitos.
- Usei `[0-9]` em vez de `\d` porque `\d` também aceita dígitos de outros alfabetos, como os árabes `٣`. O enunciado pede "dígitos de 0 a 9".

#### `normalizar`

```python
def normalizar(registro):
    pedido = {campo: valor.strip() for campo, valor in registro.items() if campo != "linha"}
    pedido["status"] = pedido["status"].upper()
    pedido["linha"] = registro["linha"]
    return pedido
```
- `registro.items()` percorre os pares (campo, valor) do dicionário.
- `valor.strip()` remove espaços, tabs e quebras **só nas pontas**. `"  Ana  Maria  "` vira `"Ana  Maria"`: o espaço do meio fica, como pede o enunciado ("não altere o conteúdo interno").
- Pulamos a chave `"linha"`, porque ela é um número (`int`) e números não têm `.strip()`. Depois a colocamos de volta.
- `.upper()` passa para maiúsculas: `"aprovado"` vira `"APROVADO"`.
- A função cria um **dicionário novo** em vez de mudar o original. Assim o registro lido do arquivo continua intacto, o que evita surpresas.

#### As funções de cada campo

Todas seguem o mesmo molde: recebem o texto, devolvem a mensagem de erro ou `None`. Cada mensagem começa com o nome do campo, como pede o enunciado (`"email: formato inválido"`).

```python
def erro_obrigatorio(campo, valor):
    if valor == "":
        return f"{campo}: obrigatório"
    return None
```
- Usada para `pedido_id` e `cliente`, que só precisam não estar vazios. Recebe o nome do campo para montar a mensagem.

```python
def erro_email(email):
    if email == "":
        return "email: obrigatório"
    if email.count("@") != 1:
        return "email: formato inválido"
    usuario, dominio = email.split("@")
    if usuario == "" or dominio == "" or any(caractere.isspace() for caractere in email):
        return "email: formato inválido"
    return None
```
- `count("@") != 1` recusa zero ou mais de um `@`.
- `email.split("@")` quebra em duas partes. Como já sabemos que há exatamente um `@`, sempre saem duas, e podemos fazer `usuario, dominio = ...` (isso se chama **desempacotamento**).
- `any(...)` é verdadeiro se **algum** caractere for espaço. `isspace()` pega espaço, tab e outros espaços invisíveis.
- Não exigimos ponto no domínio (`a@b` é aceito), como diz o enunciado.

```python
def erro_valor(valor):
    if valor == "":
        return "valor: obrigatório"
    if not PADRAO_VALOR.fullmatch(valor):
        return "valor: formato inválido (use 10, 10.5 ou 10.50)"
    if Decimal(valor) <= 0:
        return "valor: deve ser maior que zero"
    return None
```
- `fullmatch` exige que o texto **inteiro** siga o padrão. Com `match`, `"10abc"` passaria, porque o começo `"10"` combina.
- Por que regex antes do `Decimal`? Porque `Decimal("1e3")`, `Decimal("NaN")` e `Decimal("-5")` funcionam sem erro. A regex barra esses formatos antes.
- Depois da regex, o texto com certeza é um número válido, então `Decimal(valor)` nunca falha. Só falta conferir se é positivo: `0` e `0.00` são recusados.

```python
def erro_data(texto, data_referencia):
    if texto == "":
        return "data_pedido: obrigatória"
    if not PADRAO_DATA.fullmatch(texto):
        return "data_pedido: formato inválido (use AAAA-MM-DD)"
    try:
        data = date.fromisoformat(texto)
    except ValueError:
        return "data_pedido: data inexistente"
    if data > data_referencia:
        return "data_pedido: posterior à data de referência"
    return None
```
- Primeiro a regex confere o **formato**. Ela é necessária porque, a partir do Python 3.11, `date.fromisoformat` também aceita `"20261030"`, e o enunciado pede o formato exato `AAAA-MM-DD`.
- `date.fromisoformat` transforma o texto numa data. Se a data não existir (`2026-02-30`, mês 13, 29 de fevereiro em ano não bissexto), ela lança `ValueError`, que capturamos com `try/except`.
- Datas podem ser comparadas com `>`. Uma data **igual** à referência passa, porque `>` é "estritamente maior".
- `data_referencia` vem de fora, como parâmetro. Assim os testes podem usar uma data fixa (30/10/2026) e não dependem do dia em que são rodados.

```python
def erro_status(status):
    if status == "":
        return "status: obrigatório"
    if status not in STATUS_PERMITIDOS:
        return "status: inválido (use PENDENTE, APROVADO ou CANCELADO)"
    return None
```
- O status já chega em maiúsculas, graças ao `normalizar`. Por isso `"aprovado"` é aceito.

#### `validar_campos`: juntando tudo

```python
def validar_campos(pedido, data_referencia):
    erros = [
        erro_obrigatorio("pedido_id", pedido["pedido_id"]),
        erro_obrigatorio("cliente", pedido["cliente"]),
        erro_email(pedido["email"]),
        erro_valor(pedido["valor"]),
        erro_data(pedido["data_pedido"], data_referencia),
        erro_status(pedido["status"]),
    ]
    return [erro for erro in erros if erro is not None]
```
- Chama **todas** as funções, sem parar em nenhuma. O resultado é uma lista de 6 itens, cada um sendo uma mensagem ou `None`.
- A compreensão de lista no final **filtra** os `None`, sobrando só os erros de verdade.
- Lista vazia = pedido válido.
- Cada campo gera no máximo **uma** mensagem, então a mesma violação nunca aparece duas vezes, como pede o enunciado.
- A duplicidade de ID **não** está aqui. Para saber se um ID é repetido, é preciso olhar **todos** os pedidos, e esta função só enxerga um. Isso fica para o 3b.

### Os testes (`tests/test_validacao.py`)

A função auxiliar `registro(**campos)` cria um pedido válido e troca só o que o teste informar. Por exemplo, `registro(email="sem-arroba")` é um pedido válido com o e-mail errado. Assim cada teste mostra só o que importa.
- `**campos` recebe argumentos nomeados como um dicionário.
- `base.update(campos)` sobrescreve os campos informados.

`with self.subTest(valor=valor):` testa vários exemplos num mesmo teste. Se um falhar, o `unittest` mostra **qual** valor falhou e continua testando os outros.

| Teste | O que confere | Cenário do enunciado |
|---|---|---|
| `test_t01_remove_espacos_e_status_maiusculo` | `"  PED-001 "` vira `"PED-001"`, `" aprovado "` vira `"APROVADO"`, e o pedido fica sem erros | T01 |
| `test_nao_altera_conteudo_interno` | `"  Ana  Maria  "` vira `"Ana  Maria"` | regra de normalização |
| `test_t02_email_valor_e_status_invalidos` | 3 erros, um de cada campo | T02 (a contagem como um único inválido vem no 3b) |
| `test_linha_toda_vazia_acumula_erros_de_todos_os_campos` | `,,,,,` gera 6 erros | linha só com separadores |
| `test_emails_validos` / `test_emails_invalidos` | 3 aceitos, 8 recusados (`a@@b.com`, `@alfa.com`, espaço, tab...) | regra do e-mail |
| `test_valores_validos` / `test_valores_invalidos` | 4 aceitos, 13 recusados (`0`, `-10`, `10,50`, `1e3`, `NaN`...) | regra do valor |
| `test_t04_*` | igual à referência aceita, futura recusada, 30/02 recusada | T04 |
| `test_formato_errado_e_rejeitado` | `30/10/2026`, `20261030` recusados | formato exato |

### Execução

```
> python -m unittest discover
..............................
Ran 30 tests in 0.026s
OK
```

O pedido PED-003 do exemplo do enunciado, com espaços e status minúsculo adicionados de propósito:
```
{'pedido_id': 'PED-003', 'cliente': 'Gama', 'email': 'sem-arroba', 'valor': '20.00',
 'data_pedido': '2026-10-30', 'status': 'PENDENTE', 'linha': 4}
['email: formato inválido']
```
A mensagem é exatamente a do "Resultado esperado" do enunciado.

Um pedido com vários problemas, mostrando o acúmulo:
```
['cliente: obrigatório', 'valor: formato inválido (use 10, 10.5 ou 10.50)',
 'data_pedido: data inexistente', 'status: inválido (use PENDENTE, APROVADO ou CANCELADO)']
```

### Decisões para anotar no registro

- **Funções devolvem a mensagem em vez de lançar exceção:** permite acumular todos os erros da linha.
- **Regex antes do `Decimal` e do `fromisoformat`:** os dois aceitam formatos que o enunciado proíbe (`1e3`, `NaN`, `20261030`).
- **`[0-9]` em vez de `\d`:** evita aceitar dígitos de outros alfabetos.
- **Campo vazio tem mensagem própria ("obrigatório"):** fica mais claro para quem vai corrigir do que "formato inválido".
- **Data de referência como parâmetro:** deixa os testes independentes do dia em que rodam.

### Pergunta para conferir o entendimento

O valor `"007.5"` é aceito ou recusado? E o `" 10.50 "`, com espaços nas pontas? Pense na ordem: primeiro o `normalizar`, depois o `erro_valor`.

**Resposta:** os dois são **aceitos**. `"007.5"` combina com a regex (`[0-9]+` aceita `007`, depois `.5`) e `Decimal("007.5")` é 7.5, que é positivo. O enunciado não proíbe zeros à esquerda. Já `" 10.50 "` perde os espaços no `normalizar` e chega ao `erro_valor` como `"10.50"`. Se chamássemos `erro_valor` direto com espaços, ele recusaria, porque `fullmatch` não aceita espaço. Por isso a ordem importa.

---

## Pedaço 3b: IDs duplicados e separar válidos de inválidos

### O que e por quê

Até aqui, cada pedido era conferido sozinho. Mas "o ID é único?" é uma pergunta que **não dá para responder olhando um pedido só**: é preciso ver o arquivo inteiro. Por isso a duplicidade ficou para um passo separado.

Regras do enunciado:
- **todas** as ocorrências de um ID repetido são inválidas, inclusive a primeira;
- a duplicidade vale mesmo se uma das ocorrências tiver outros erros;
- a comparação diferencia maiúsculas (`ped-001` e `PED-001` são IDs diferentes);
- ID vazio recebe só "obrigatório", sem o erro de duplicado.

A lógica tem **duas passadas**:
1. Primeiro, contar quantas vezes cada ID aparece no arquivo todo.
2. Depois, percorrer os pedidos de novo e marcar como duplicado quem tem contagem maior que 1.

Por que não dá para fazer numa passada só? Porque, quando lemos a primeira ocorrência de `PED-001`, ainda não sabemos que existe uma segunda lá embaixo. E o enunciado pede que a primeira também seja inválida.

### O código

```python
from collections import Counter
```
- `Counter` é um dicionário especial que **conta** coisas. `Counter(["A", "B", "A"])` vira `{"A": 2, "B": 1}`.

```python
def ids_duplicados(pedidos):
    contagem = Counter(pedido["pedido_id"] for pedido in pedidos if pedido["pedido_id"] != "")
    return {pedido_id for pedido_id, quantidade in contagem.items() if quantidade > 1}
```
- A parte dentro do `Counter(...)` é uma **expressão geradora**: parecida com a compreensão de lista, mas sem os colchetes. Ela entrega os IDs um por um, sem montar uma lista inteira na memória.
- `if pedido["pedido_id"] != ""` deixa os IDs vazios de fora da contagem. Assim dois IDs vazios **não** viram "duplicados", e recebem só o erro de obrigatório.
- No final, uma compreensão de conjunto guarda só os IDs com contagem maior que 1.
- Devolver um **conjunto** (`set`) é proposital: perguntar `x in conjunto` é muito rápido, mesmo com milhares de IDs.
- A comparação de textos em Python já diferencia maiúsculas, então não precisamos fazer nada para cumprir essa regra. Basta **não** usar `.upper()` no ID.

```python
def validar_pedidos(registros, data_referencia):
    pedidos = [normalizar(registro) for registro in registros]
    duplicados = ids_duplicados(pedidos)
```
- Primeiro normaliza **todos**. A ordem importa: `"  PED-001  "` e `"PED-001"` só são reconhecidos como o mesmo ID depois de remover os espaços.
- Depois calcula o conjunto de duplicados (a primeira passada).

```python
    validos = []
    invalidos = []
    for pedido in pedidos:
        erros = validar_campos(pedido, data_referencia)
        if pedido["pedido_id"] in duplicados:
            erros.append("pedido_id: duplicado no arquivo")
```
- A segunda passada. Para cada pedido, pega os erros dos campos (do 3a) e, se o ID estiver no conjunto de duplicados, **acrescenta** mais um erro.
- Como os dois erros são somados na mesma lista, um pedido duplicado **e** com e-mail ruim mostra os dois. É o que o T03 pede.
- Um ID vazio nunca está em `duplicados`, então ele fica só com "obrigatório".

```python
        if erros:
            invalidos.append({"linha": pedido["linha"], "pedido_id": pedido["pedido_id"], "erros": erros})
        else:
            validos.append(pedido)

    return validos, invalidos
```
- Lista com erros: o pedido vai para `invalidos`, já no formato que o relatório JSON vai usar (`linha`, `pedido_id` normalizado e `erros`).
- Lista vazia: o pedido vai inteiro para `validos`. A etapa 4 vai precisar do `valor` e do `status` deles para somar os aprovados.
- Um pedido com 3 erros entra **uma vez só** em `invalidos`. É isso que garante "uma linha com vários erros conta como um único registro inválido".
- Como percorremos os pedidos na ordem do arquivo, os inválidos já saem **na ordem das linhas**, como pede o enunciado.
- `return validos, invalidos` devolve **duas** coisas de uma vez (na verdade, uma tupla). Quem chama pode desempacotar: `validos, invalidos = validar_pedidos(...)`.
- Repare que `len(validos) + len(invalidos)` é sempre igual ao número de registros, porque cada pedido cai em exatamente uma das listas. Isso garante a regra `total_registros = registros_validos + registros_invalidos`.

### Os testes novos

| Teste | O que confere | Cenário |
|---|---|---|
| `test_encontra_somente_os_repetidos` | `A, B, A` devolve só `{"A"}` | duplicidade |
| `test_diferencia_maiusculas` | `ped-001` e `PED-001` não são duplicados | regra do enunciado |
| `test_ids_vazios_nao_contam_como_duplicados` | dois IDs vazios não são duplicados | regra do enunciado |
| `test_t02_varios_erros_contam_como_um_registro_invalido` | 3 erros, mas 1 item só em `invalidos` | T02 completo |
| `test_t03_duplicado_invalida_todas_as_ocorrencias` | as linhas 2 e 4 ficam inválidas, e a 4 mostra o erro de e-mail **e** o de duplicado | T03 |
| `test_duplicado_detectado_depois_de_remover_espacos` | `"  PED-001  "` é duplicado de `"PED-001"` | normalização antes da duplicidade |
| `test_id_vazio_recebe_so_erro_de_obrigatorio` | `""` e `" "` recebem só "obrigatório", e o `pedido_id` sai como `""` | regra do enunciado |
| `test_exemplo_do_enunciado` | os 3 pedidos do enunciado dão 2 válidos e exatamente o inválido esperado | exemplo de aceitação |

O `_` em `_, invalidos = validar_pedidos(...)` é uma convenção para "não vou usar este valor".

### Execução

```
> python -m unittest discover
......................................
Ran 38 tests in 0.062s
OK
```

### Decisões para anotar no registro

- **Duas passadas (contar, depois marcar):** é a forma mais simples de invalidar também a primeira ocorrência.
- **Duplicidade depois da normalização:** espaços nas pontas não podem esconder um ID repetido.
- **IDs vazios fora da contagem:** evita um erro duplicado sem sentido, como pede o enunciado.
- **Mensagem do duplicado no fim da lista de erros:** os erros de campo vêm primeiro, na ordem das colunas. O enunciado diz que a ordem das mensagens é livre.

### Pergunta para conferir o entendimento

Um arquivo tem três pedidos com o ID `PED-010`. O primeiro está perfeito, o segundo tem valor `0` e o terceiro tem e-mail sem `@`. Quantos itens ficam em `invalidos`? E quantos erros tem cada um?

**Resposta:** ficam **3** itens em `invalidos`, porque todas as ocorrências de um ID repetido são inválidas. Os erros se **somam**, então:
- 1º (perfeito): 1 erro, `pedido_id: duplicado no arquivo`;
- 2º (valor 0): 2 erros, `valor: deve ser maior que zero` e o de duplicado;
- 3º (sem @): 2 erros, `email: formato inválido` e o de duplicado.

O erro de duplicado é **acrescentado** (`erros.append`) aos erros dos campos, e não os substitui.
