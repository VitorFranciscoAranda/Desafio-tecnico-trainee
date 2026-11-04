# Etapa 8: documentação e entrega

## O que e por quê

O código está pronto, mas o avaliador precisa conseguir **instalar, executar e entender** o projeto sem falar com você. "Documentação e reprodução" vale 15% da nota, e "investigação e aprendizado" vale mais 20%, avaliados principalmente pelo registro de decisões.

Nesta etapa foram criados ou atualizados:

| Arquivo | Para quê |
|---|---|
| `README.md` | o "manual" do projeto: o que é, como instalar, como rodar, argumentos, códigos de saída, formatos, estrutura, testes, limitações e próximos passos |
| `docs/registro-decisoes.md` | decisões e motivos, uma dificuldade concreta, aprendizado, tempo, próximos passos e uso de IA |
| `requirements.txt` | declara que não há dependências (o enunciado pede `requirements.txt` ou o aviso no README; fizemos os dois) |
| `docs/evidencias/testes-ultima-execucao.txt` | saída real da última execução dos testes, gerada de novo com a versão final |

Também apaguei os arquivos `.gitkeep` de `dados/` e `saida/`. Eles só existiam para o git guardar as pastas vazias, e agora elas têm arquivos.

## Como o README foi organizado

Segui a lista do enunciado ("Conteúdo obrigatório do README") e a ordem em que um avaliador lê:

1. **O que é** (visão geral em 4 passos, um por módulo).
2. **O que preciso ter** (pré-requisitos: Python 3.11+, sem dependências).
3. **Como instalo** (clonar, conferir a versão; o ambiente virtual é opcional).
4. **Como rodo** (exemplo, demonstração, `--help`), com a saída esperada logo abaixo do comando, para a pessoa conferir se deu certo.
5. **O que cada argumento faz** e **o que cada código de saída significa**, incluindo o comportamento da data padrão, que o enunciado pede para documentar.
6. **Formatos** de entrada e de saída.
7. **Onde fica cada coisa** (estrutura).
8. **Como testo** (comando único + link para a matriz e para a evidência).
9. **O que não está perfeito** (limitações) e **o que faria depois** (próximos passos).

Dois cuidados que valem comentar numa entrevista:
- **O aviso sobre `-m`:** foi o erro que você mesmo encontrou ao rodar pelo F5. Se aconteceu com você, pode acontecer com o avaliador, então o README avisa antes.
- **Limitações à vista:** o enunciado pede que "falhas e limitações permaneçam visíveis". Esconder limitações passa a impressão de que você não as percebeu.

## O registro de decisões

O enunciado pede, em até duas páginas: decisões e motivos, **uma dificuldade concreta com hipóteses e tentativas**, o que você precisou aprender, estimativa de tempo, próximos passos e o uso de IA com pelo menos uma sugestão conferida.

- **Decisões:** uma tabela com 13 decisões tomadas ao longo das etapas. Todas já apareceram nas seções "Decisões para anotar no registro" dos arquivos das etapas 2 a 7.
- **Dificuldade concreta:** usei o `ModuleNotFoundError` que você encontrou. É um caso **real**, com três hipóteses e o raciocínio para descartar duas delas. Um caso real é bem mais fácil de explicar numa entrevista do que um inventado.
- **Uso de IA:** descreve como a IA foi usada e dá quatro exemplos de verificação. O enunciado pede pelo menos um.

### ✏️ O que **você** precisa completar

Deixei marcados com ✏️ os trechos que só você pode escrever com honestidade:
- **"O que precisei aprender":** deixei uma lista de sugestões, mas reescreva com as suas palavras, citando o que foi novo **para você**.
- **"Estimativa de tempo":** coloque o seu tempo real.
- **A nota no topo do arquivo:** apague depois de revisar.

Também vale ler o texto inteiro e mudar o que não soar como você. O avaliador pode perguntar sobre qualquer frase dele.

## Conferência final: o projeto funciona numa pasta limpa?

O enunciado diz que as instruções precisam funcionar "a partir de uma pasta recém-extraída ou clonada". Para testar isso de verdade:

1. Copiei para uma pasta temporária **só os arquivos que iriam para o repositório**, ou seja, sem o que está no `.gitignore` (`.vscode/`, `docs/enunciado/`, `__pycache__`).
2. Nessa cópia, rodei exatamente os comandos do README:

```
> python -m pip install -r requirements.txt
(termina sem instalar nada)
> python -m app --entrada dados/pedidos.csv --saida saida/relatorio.json --data-referencia 2026-10-30
  Total aprovado:       150.50
  Relatório gravado em: saida\relatorio.json
> python -m unittest discover
OK
```

Tudo funcionou. Isso garante que o projeto não depende de nada que só existe no seu computador.

Execução final dos testes, gravada em `docs/evidencias/testes-ultima-execucao.txt`:
```
Ran 63 tests in 0.187s
OK
```

## Lista de verificação do enunciado

| Item exigido | Onde está | Situação |
|---|---|---|
| Código-fonte | `app/` | ✓ |
| Dependências declaradas ou indicação de biblioteca padrão | `requirements.txt` e README | ✓ |
| README | `README.md` | ✓ |
| Registro de decisões e uso de IA | `docs/registro-decisoes.md` | ✓ (falta você completar os trechos ✏️) |
| Testes e matriz de cenários | `tests/`, `docs/matriz-testes.md` | ✓ |
| CSV de exemplo | `dados/pedidos.csv` | ✓ |
| CSV de demonstração | `dados/pedidos_demonstracao.csv` | ✓ |
| Relatório da demonstração | `saida/relatorio_demonstracao.json` | ✓ |
| Evidência da última execução dos testes | `docs/evidencias/testes-ultima-execucao.txt` | ✓ |
| Sem ambientes virtuais, caches, credenciais ou dados reais | `.gitignore`; dados fictícios | ✓ |
| Entrega identificada com seu nome | topo do README | ✓ |

## O que falta para entregar

Essas ações são suas, porque envolvem a sua conta e o envio para a empresa:
1. Completar os trechos ✏️ do registro.
2. Fazer o commit e o push para o GitHub (posso fazer quando você pedir) e conferir se o repositório está acessível ao avaliador. Se for privado, é preciso dar acesso a ele, ou então enviar um ZIP.
3. Enviar o link pelo canal do processo seletivo, dentro do prazo de 48 horas.

## Pergunta para conferir o entendimento

Na entrevista, o avaliador pede: "mude a regra para aceitar até **três** casas decimais no valor". Quais arquivos você mudaria? E qual teste deveria começar a falhar antes de você ajustá-lo?
