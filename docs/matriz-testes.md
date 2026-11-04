# Matriz de testes

Comando (executado na pasta raiz do projeto):

```
python -m unittest discover -v
```

Resumo real da última execução (Windows 11, Python 3.12.10, 2026-11-04): **63 testes, 63 passaram, 0 falharam.** A saída completa está em [`evidencias/testes-ultima-execucao.txt`](evidencias/testes-ultima-execucao.txt).

## Cenários obrigatórios e escolhidos

| ID | Cenário | Resultado esperado | Teste(s) correspondente(s) | Situação |
|---|---|---|---|---|
| T01 | Pedido válido com espaços externos e status minúsculo | Aceito; espaços removidos e status em maiúsculas | `test_validacao.TestNormalizar.test_t01_remove_espacos_e_status_maiusculo` | Passou |
| T02 | E-mail, valor e status inválidos na mesma linha | 3 erros, um registro inválido | `test_validacao.TestValidarCampos.test_t02_email_valor_e_status_invalidos`, `test_validacao.TestValidarPedidos.test_t02_varios_erros_contam_como_um_registro_invalido` | Passou |
| T03 | ID duplicado, uma ocorrência com outro erro | Todas as ocorrências inválidas; a com erro mostra os dois | `test_validacao.TestValidarPedidos.test_t03_duplicado_invalida_todas_as_ocorrencias` | Passou |
| T04 | Data impossível, futura e igual à referência (2026-10-30) | Impossível e futura recusadas; igual aceita | `test_validacao.TestData.test_t04_data_impossivel_e_rejeitada`, `test_t04_data_futura_e_rejeitada`, `test_t04_data_igual_a_referencia_e_aceita` | Passou |
| T05 | Soma com aprovados, pendentes, cancelados e aprovado inválido; 0.10 + 0.20 | Só aprovados válidos somados; `"0.30"` | `test_relatorio.TestTotalAprovado.test_t05_soma_somente_aprovados`, `test_t05_sem_erro_de_arredondamento`, `test_relatorio.TestMontarRelatorio.test_t05_invalidos_ficam_fora_da_soma`, `test_cli.TestExecucaoCompleta.test_t05_aprovado_invalido_fica_fora_da_soma` | Passou |
| T06 | Arquivo só com cabeçalho | Contagens zero, `"0.00"`, `invalidos: []` | `test_cli.TestExecucaoCompleta.test_t06_somente_cabecalho`, `test_relatorio.TestMontarRelatorio.test_t06_sem_registros`, `test_leitura.TestLerPedidos.test_somente_cabecalho_tem_zero_registros` | Passou |
| T07 | Arquivo inexistente; coluna obrigatória ausente | Falha controlada, código ≠ 0, sem traceback, sem relatório | `test_cli.TestFalhasControladas.test_t07_arquivo_inexistente`, `test_t07_coluna_obrigatoria_ausente` | Passou |
| T08 | Execução completa pelo comando publicado com CSV temporário | Código 0 e JSON igual ao resultado esperado do enunciado | `test_cli.TestExecucaoCompleta.test_t08_comando_publicado_gera_json_esperado` | Passou |
| T09 *(escolhido)* | Arquivo com codificação inválida (Latin-1) | Erro estrutural citando UTF-8, código ≠ 0, sem relatório | `test_cli.TestFalhasControladas.test_t09_codificacao_invalida`, `test_leitura.TestLerPedidos.test_codificacao_invalida` | Passou |
| T10 *(escolhido)* | Mesmo arquivo como entrada e saída, inclusive por caminho diferente | Recusado, código ≠ 0, CSV intacto | `test_cli.TestFalhasControladas.test_t10_entrada_igual_a_saida`, `test_t10_mesmo_arquivo_escrito_de_outro_jeito` | Passou |

### Riscos cobertos pelos cenários escolhidos

- **T09, codificação inválida:** arquivos exportados do Excel ou de editores antigos costumam vir em Latin-1/ANSI. Sem esse cuidado, o programa poderia quebrar com um traceback ou ler acentos errados em silêncio.
- **T10, entrada igual à saída:** um erro de digitação no terminal poderia substituir o CSV original pelo relatório, e esse dado não teria como ser recuperado.

## Outros testes (regras do contrato)

| Área | O que cobrem | Arquivo |
|---|---|---|
| Cabeçalho | ordem livre, coluna extra, coluna duplicada, nome sensível a maiúsculas | `test_leitura.py` |
| Leitura | número da linha física, aspas com vírgula, `,,,,,` vira registro, linha de espaços ignorada, BOM do Excel, arquivo vazio, quantidade de campos, CSV malformado | `test_leitura.py` |
| E-mail | 3 válidos e 8 inválidos (sem `@`, dois `@`, lado vazio, espaço, tab) | `test_validacao.py` |
| Valor | 4 válidos e 13 inválidos (`0`, sinal, vírgula, `1e3`, `NaN`, `Infinity`, 3 casas) | `test_validacao.py` |
| Data | formatos errados (`30/10/2026`, `20261030`) | `test_validacao.py` |
| Duplicidade | maiúsculas diferenciam, IDs vazios não contam, duplicado depois de remover espaços | `test_validacao.py` |
| Relatório | duas casas, `"0.00"`, contagens, gravação UTF-8, criação de pasta, substituição, falha de gravação | `test_relatorio.py` |
| Terminal | `--help`, argumento obrigatório, data de referência inválida, data padrão = hoje, entrada não modificada, aviso sobre relatório anterior | `test_cli.py` |
| Demonstração | o relatório entregue em `saida/relatorio_demonstracao.json` é igual ao que o código gera hoje | `test_cli.py` |

## Verificação dos próprios testes (teste de mutação manual)

Para conferir se os testes realmente detectam erros, quebrei de propósito quatro regras numa **cópia** do código e rodei os testes nela. O código do projeto não foi alterado.

| Regra quebrada de propósito | Testes que falharam |
|---|---|
| Data igual à referência passa a ser recusada (`>` virou `>=`) | 3 (T04, T08 e exemplo do enunciado) |
| Duplicado só a partir de 3 ocorrências | 3 (incluindo T03) |
| Soma inclui pedidos pendentes | 3 (incluindo os de T05) |
| Status deixa de ser convertido para maiúsculas | 2 (T01 e T05 de ponta a ponta) |

Em todos os casos a suíte falhou, ou seja, os testes protegem essas regras.

## Limitações conhecidas dos testes

- Não há medição de cobertura de código (o enunciado não exige percentual).
- A falha de gravação foi simulada com um caminho que é uma pasta. Disco cheio e falta de permissão não foram simulados.
- Os testes rodaram só no Windows. O código usa apenas a biblioteca padrão e `pathlib`, então deve funcionar em Linux e macOS, mas isso não foi verificado.
