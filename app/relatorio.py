"""Montagem e gravação do relatório JSON."""

import json
from decimal import Decimal
from pathlib import Path

DUAS_CASAS = Decimal("0.01")


class ErroGravacao(Exception):
    """Não foi possível gravar o relatório no caminho de saída."""


def total_aprovado(validos):
    """Soma os valores dos pedidos válidos com status APROVADO. Devolve texto com 2 casas."""
    total = Decimal("0")
    for pedido in validos:
        if pedido["status"] == "APROVADO":
            total += Decimal(pedido["valor"])
    return str(total.quantize(DUAS_CASAS))


def montar_relatorio(validos, invalidos, data_referencia):
    """Monta o dicionário do relatório no formato pedido pelo enunciado."""
    return {
        "data_referencia": data_referencia.isoformat(),
        "total_registros": len(validos) + len(invalidos),
        "registros_validos": len(validos),
        "registros_invalidos": len(invalidos),
        "total_aprovado": total_aprovado(validos),
        "invalidos": invalidos,
    }


def gravar_relatorio(relatorio, caminho):
    """Grava o relatório em JSON (UTF-8), criando a pasta se for preciso.

    Grava primeiro num arquivo temporário e só no final o renomeia para o nome
    definitivo. Assim, se algo falhar no meio, nunca fica um relatório pela metade.
    """
    caminho = Path(caminho)
    temporario = caminho.with_name(caminho.name + ".tmp")
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        temporario.replace(caminho)
    except OSError as erro:
        temporario.unlink(missing_ok=True)
        raise ErroGravacao(f"não foi possível gravar o relatório em {caminho}: {erro}")
