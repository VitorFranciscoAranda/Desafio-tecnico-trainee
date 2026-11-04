"""Regras de validação dos pedidos."""

import re
from collections import Counter
from datetime import date
from decimal import Decimal

STATUS_PERMITIDOS = ("PENDENTE", "APROVADO", "CANCELADO")

# [0-9] em vez de \d: \d também aceita dígitos de outros alfabetos (ex.: árabes).
PADRAO_VALOR = re.compile(r"[0-9]+(\.[0-9]{1,2})?")
PADRAO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def normalizar(registro):
    """Devolve uma cópia do registro sem espaços nas extremidades e com status em maiúsculas."""
    pedido = {campo: valor.strip() for campo, valor in registro.items() if campo != "linha"}
    pedido["status"] = pedido["status"].upper()
    pedido["linha"] = registro["linha"]
    return pedido


# Cada função abaixo confere um campo e devolve a mensagem de erro, ou None se estiver certo.

def erro_obrigatorio(campo, valor):
    if valor == "":
        return f"{campo}: obrigatório"
    return None


def erro_email(email):
    if email == "":
        return "email: obrigatório"
    if email.count("@") != 1:
        return "email: formato inválido"
    usuario, dominio = email.split("@")
    if usuario == "" or dominio == "" or any(caractere.isspace() for caractere in email):
        return "email: formato inválido"
    return None


def erro_valor(valor):
    if valor == "":
        return "valor: obrigatório"
    if not PADRAO_VALOR.fullmatch(valor):
        return "valor: formato inválido (use 10, 10.5 ou 10.50)"
    if Decimal(valor) <= 0:
        return "valor: deve ser maior que zero"
    return None


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


def erro_status(status):
    if status == "":
        return "status: obrigatório"
    if status not in STATUS_PERMITIDOS:
        return "status: inválido (use PENDENTE, APROVADO ou CANCELADO)"
    return None


def validar_campos(pedido, data_referencia):
    """Confere todos os campos de um pedido já normalizado e devolve a lista de erros."""
    erros = [
        erro_obrigatorio("pedido_id", pedido["pedido_id"]),
        erro_obrigatorio("cliente", pedido["cliente"]),
        erro_email(pedido["email"]),
        erro_valor(pedido["valor"]),
        erro_data(pedido["data_pedido"], data_referencia),
        erro_status(pedido["status"]),
    ]
    return [erro for erro in erros if erro is not None]


def ids_duplicados(pedidos):
    """Devolve o conjunto de IDs não vazios que aparecem mais de uma vez."""
    contagem = Counter(pedido["pedido_id"] for pedido in pedidos if pedido["pedido_id"] != "")
    return {pedido_id for pedido_id, quantidade in contagem.items() if quantidade > 1}


def validar_pedidos(registros, data_referencia):
    """Normaliza e valida todos os registros lidos do arquivo.

    Devolve duas listas: os pedidos válidos e os inválidos. Cada inválido é um
    dicionário com "linha", "pedido_id" e "erros", na ordem do arquivo.
    """
    pedidos = [normalizar(registro) for registro in registros]
    duplicados = ids_duplicados(pedidos)

    validos = []
    invalidos = []
    for pedido in pedidos:
        erros = validar_campos(pedido, data_referencia)
        if pedido["pedido_id"] in duplicados:
            erros.append("pedido_id: duplicado no arquivo")

        if erros:
            invalidos.append({"linha": pedido["linha"], "pedido_id": pedido["pedido_id"], "erros": erros})
        else:
            validos.append(pedido)

    return validos, invalidos
