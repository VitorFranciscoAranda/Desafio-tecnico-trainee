"""Leitura e verificação da estrutura do arquivo CSV de pedidos."""

import csv
from pathlib import Path

COLUNAS_OBRIGATORIAS = ("pedido_id", "cliente", "email", "valor", "data_pedido", "status")


class ErroEstrutural(Exception):
    """Problema no arquivo que impede o processamento (ex.: coluna ausente)."""


def validar_cabecalho(cabecalho):
    """Confere a lista de nomes do cabeçalho. Lança ErroEstrutural se houver problema."""
    duplicadas = sorted({nome for nome in cabecalho if cabecalho.count(nome) > 1})
    if duplicadas:
        raise ErroEstrutural(f"cabeçalho com colunas duplicadas: {', '.join(duplicadas)}")

    ausentes = [nome for nome in COLUNAS_OBRIGATORIAS if nome not in cabecalho]
    if ausentes:
        raise ErroEstrutural(f"coluna obrigatória ausente: {', '.join(ausentes)}")


def linha_em_branco(campos):
    """Verdadeiro se a linha não tem nenhum separador nem conteúdo."""
    return len(campos) <= 1 and "".join(campos).strip() == ""


def ler_pedidos(caminho):
    """Lê o CSV e devolve a lista de registros.

    Cada registro é um dicionário com as colunas obrigatórias (valores ainda
    sem tratamento) e a chave "linha", com o número da linha no arquivo.
    O cabeçalho é a linha 1.
    """
    caminho = Path(caminho)
    if not caminho.is_file():
        raise ErroEstrutural(f"arquivo de entrada não encontrado: {caminho}")

    registros = []
    try:
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.reader(arquivo, strict=True)

            cabecalho = next(leitor, None)
            if cabecalho is None:
                raise ErroEstrutural("arquivo vazio: o cabeçalho é obrigatório")
            validar_cabecalho(cabecalho)

            for campos in leitor:
                if linha_em_branco(campos):
                    continue
                if len(campos) != len(cabecalho):
                    raise ErroEstrutural(
                        f"linha {leitor.line_num}: esperados {len(cabecalho)} campos, "
                        f"encontrados {len(campos)}"
                    )
                registro = {nome: campos[cabecalho.index(nome)] for nome in COLUNAS_OBRIGATORIAS}
                registro["linha"] = leitor.line_num
                registros.append(registro)
    except UnicodeDecodeError:
        raise ErroEstrutural("o arquivo de entrada não está codificado em UTF-8")
    except csv.Error as erro:
        raise ErroEstrutural(f"CSV malformado na linha {leitor.line_num}: {erro}")
    except OSError as erro:
        raise ErroEstrutural(f"não foi possível ler o arquivo de entrada: {erro}")

    return registros
