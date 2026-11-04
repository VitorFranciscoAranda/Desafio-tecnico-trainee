"""Ponto de entrada da aplicação: executado com "python -m app"."""

import argparse
import sys
from datetime import date
from pathlib import Path

from app.leitura import ErroEstrutural, ler_pedidos
from app.relatorio import ErroGravacao, gravar_relatorio, montar_relatorio
from app.validacao import PADRAO_DATA, validar_pedidos


def data_valida(texto):
    """Converte o texto de --data-referencia em date. O argparse chama esta função."""
    try:
        if not PADRAO_DATA.fullmatch(texto):
            raise ValueError
        return date.fromisoformat(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"data inválida '{texto}' (use uma data real no formato AAAA-MM-DD)")


def criar_parser():
    """Define os argumentos aceitos pelo programa e o texto do --help."""
    parser = argparse.ArgumentParser(
        prog="python -m app",
        description="Confere um arquivo CSV de pedidos e gera um relatório JSON.",
        epilog="Exemplo: python -m app --entrada dados/pedidos.csv "
        "--saida saida/relatorio.json --data-referencia 2026-10-30",
    )
    parser.add_argument("--entrada", required=True, type=Path,
                        help="caminho do arquivo CSV de pedidos (UTF-8)")
    parser.add_argument("--saida", required=True, type=Path,
                        help="caminho do relatório JSON; a pasta é criada se não existir")
    parser.add_argument("--data-referencia", type=data_valida,
                        help="data AAAA-MM-DD; pedidos com data posterior são inválidos "
                        "(padrão: a data de hoje no computador)")
    return parser


def mesmo_arquivo(entrada, saida):
    """Verdadeiro se os dois caminhos apontam para o mesmo arquivo existente."""
    return entrada.exists() and saida.exists() and entrada.samefile(saida)


def falhar(mensagem, saida=None):
    """Mostra o erro no terminal e devolve o código de saída de falha."""
    print(f"Erro: {mensagem}", file=sys.stderr)
    if saida is not None and saida.exists():
        print(f"Aviso: nenhum relatório foi gravado. O arquivo {saida} é de uma execução "
            "anterior e não corresponde a esta.", file=sys.stderr)
    return 1


def imprimir_resumo(relatorio, saida):
    print("Conferência concluída.")
    print(f"  Data de referência:   {relatorio['data_referencia']}")
    print(f"  Total de registros:   {relatorio['total_registros']}")
    print(f"  Registros válidos:    {relatorio['registros_validos']}")
    print(f"  Registros inválidos:  {relatorio['registros_invalidos']}")
    print(f"  Total aprovado:       {relatorio['total_aprovado']}")
    print(f"  Relatório gravado em: {saida}")


def main(argv=None):
    """Coordena a execução. Devolve 0 em caso de sucesso e 1 em caso de falha."""
    hoje = date.today()  # obtida uma única vez, no início da execução
    argumentos = criar_parser().parse_args(argv)
    data_referencia = argumentos.data_referencia or hoje

    if mesmo_arquivo(argumentos.entrada, argumentos.saida):
        return falhar("--entrada e --saida apontam para o mesmo arquivo; escolha outro caminho para a saída")

    try:
        registros = ler_pedidos(argumentos.entrada)
        validos, invalidos = validar_pedidos(registros, data_referencia)
        relatorio = montar_relatorio(validos, invalidos, data_referencia)
        gravar_relatorio(relatorio, argumentos.saida)
    except (ErroEstrutural, ErroGravacao) as erro:
        return falhar(str(erro), argumentos.saida)

    imprimir_resumo(relatorio, argumentos.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
