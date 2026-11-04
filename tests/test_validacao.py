"""Testes do módulo app.validacao."""

import unittest
from datetime import date

from app.validacao import (
    erro_data,
    erro_email,
    erro_valor,
    ids_duplicados,
    normalizar,
    validar_campos,
    validar_pedidos,
)

REFERENCIA = date(2026, 10, 30)


def registro(**campos):
    """Cria um registro válido e troca só os campos informados."""
    base = {
        "pedido_id": "PED-001",
        "cliente": "Alfa",
        "email": "a@alfa.com",
        "valor": "150.50",
        "data_pedido": "2026-10-29",
        "status": "APROVADO",
        "linha": 2,
    }
    base.update(campos)
    return base


class TestNormalizar(unittest.TestCase):
    def test_t01_remove_espacos_e_status_maiusculo(self):
        pedido = normalizar(registro(pedido_id="  PED-001 ", cliente=" Alfa ", status=" aprovado "))
        self.assertEqual(pedido["pedido_id"], "PED-001")
        self.assertEqual(pedido["cliente"], "Alfa")
        self.assertEqual(pedido["status"], "APROVADO")
        self.assertEqual(pedido["linha"], 2)
        self.assertEqual(validar_campos(pedido, REFERENCIA), [])

    def test_nao_altera_conteudo_interno(self):
        pedido = normalizar(registro(cliente="  Ana  Maria  "))
        self.assertEqual(pedido["cliente"], "Ana  Maria")


class TestValidarCampos(unittest.TestCase):
    def test_t02_email_valor_e_status_invalidos(self):
        pedido = normalizar(registro(email="sem-arroba", valor="-5", status="ENVIADO"))
        erros = validar_campos(pedido, REFERENCIA)
        self.assertEqual(len(erros), 3)
        self.assertTrue(erros[0].startswith("email:"))
        self.assertTrue(erros[1].startswith("valor:"))
        self.assertTrue(erros[2].startswith("status:"))

    def test_linha_toda_vazia_acumula_erros_de_todos_os_campos(self):
        pedido = normalizar(registro(pedido_id="", cliente="", email="", valor="", data_pedido="", status=""))
        self.assertEqual(len(validar_campos(pedido, REFERENCIA)), 6)


class TestEmail(unittest.TestCase):
    def test_emails_validos(self):
        for email in ["a@alfa.com", "a@b", "nome.sobrenome@empresa.com.br"]:
            with self.subTest(email=email):
                self.assertIsNone(erro_email(email))

    def test_emails_invalidos(self):
        for email in ["", "sem-arroba", "a@@b.com", "a@b@c", "@alfa.com", "a@", "a b@alfa.com", "a@al\tfa.com"]:
            with self.subTest(email=email):
                self.assertIsNotNone(erro_email(email))


class TestValor(unittest.TestCase):
    def test_valores_validos(self):
        for valor in ["10", "10.5", "10.50", "0.01"]:
            with self.subTest(valor=valor):
                self.assertIsNone(erro_valor(valor))

    def test_valores_invalidos(self):
        for valor in ["", "0", "0.00", "-10", "+10", "10,50", "10.555", "1e3", "NaN", "Infinity", ".5", "10.", "abc"]:
            with self.subTest(valor=valor):
                self.assertIsNotNone(erro_valor(valor))


class TestData(unittest.TestCase):
    def test_t04_data_igual_a_referencia_e_aceita(self):
        self.assertIsNone(erro_data("2026-10-30", REFERENCIA))

    def test_t04_data_futura_e_rejeitada(self):
        self.assertIn("posterior", erro_data("2026-10-31", REFERENCIA))

    def test_t04_data_impossivel_e_rejeitada(self):
        for texto in ["2026-02-30", "2026-13-01", "2025-02-29"]:
            with self.subTest(texto=texto):
                self.assertIn("inexistente", erro_data(texto, REFERENCIA))

    def test_formato_errado_e_rejeitado(self):
        for texto in ["30/10/2026", "20261030", "2026-1-5", "2026-10-30T10:00"]:
            with self.subTest(texto=texto):
                self.assertIn("formato", erro_data(texto, REFERENCIA))


class TestIdsDuplicados(unittest.TestCase):
    def test_encontra_somente_os_repetidos(self):
        pedidos = [{"pedido_id": "A"}, {"pedido_id": "B"}, {"pedido_id": "A"}]
        self.assertEqual(ids_duplicados(pedidos), {"A"})

    def test_diferencia_maiusculas(self):
        pedidos = [{"pedido_id": "ped-001"}, {"pedido_id": "PED-001"}]
        self.assertEqual(ids_duplicados(pedidos), set())

    def test_ids_vazios_nao_contam_como_duplicados(self):
        pedidos = [{"pedido_id": ""}, {"pedido_id": ""}]
        self.assertEqual(ids_duplicados(pedidos), set())


class TestValidarPedidos(unittest.TestCase):
    def test_t02_varios_erros_contam_como_um_registro_invalido(self):
        registros = [registro(email="sem-arroba", valor="-5", status="ENVIADO")]
        validos, invalidos = validar_pedidos(registros, REFERENCIA)
        self.assertEqual(validos, [])
        self.assertEqual(len(invalidos), 1)
        self.assertEqual(len(invalidos[0]["erros"]), 3)

    def test_t03_duplicado_invalida_todas_as_ocorrencias(self):
        registros = [
            registro(pedido_id="PED-001", linha=2),
            registro(pedido_id="PED-002", linha=3),
            registro(pedido_id="PED-001", email="sem-arroba", linha=4),
        ]
        validos, invalidos = validar_pedidos(registros, REFERENCIA)

        self.assertEqual([pedido["pedido_id"] for pedido in validos], ["PED-002"])
        self.assertEqual([item["linha"] for item in invalidos], [2, 4])
        self.assertEqual(invalidos[0]["erros"], ["pedido_id: duplicado no arquivo"])
        self.assertEqual(invalidos[1]["erros"], ["email: formato inválido", "pedido_id: duplicado no arquivo"])

    def test_duplicado_detectado_depois_de_remover_espacos(self):
        registros = [registro(pedido_id="PED-001", linha=2), registro(pedido_id="  PED-001  ", linha=3)]
        validos, invalidos = validar_pedidos(registros, REFERENCIA)
        self.assertEqual(validos, [])
        self.assertEqual(invalidos[1]["pedido_id"], "PED-001")

    def test_id_vazio_recebe_so_erro_de_obrigatorio(self):
        registros = [registro(pedido_id="", linha=2), registro(pedido_id=" ", linha=3)]
        _, invalidos = validar_pedidos(registros, REFERENCIA)
        for item in invalidos:
            self.assertEqual(item["pedido_id"], "")
            self.assertEqual(item["erros"], ["pedido_id: obrigatório"])

    def test_exemplo_do_enunciado(self):
        registros = [
            {"pedido_id": "PED-001", "cliente": "Alfa", "email": "a@alfa.com", "valor": "150.50",
             "data_pedido": "2026-10-29", "status": "APROVADO", "linha": 2},
            {"pedido_id": "PED-002", "cliente": "Beta", "email": "b@beta.com", "valor": "40",
             "data_pedido": "2026-10-30", "status": "CANCELADO", "linha": 3},
            {"pedido_id": "PED-003", "cliente": "Gama", "email": "sem-arroba", "valor": "20.00",
             "data_pedido": "2026-10-30", "status": "PENDENTE", "linha": 4},
        ]
        validos, invalidos = validar_pedidos(registros, REFERENCIA)
        self.assertEqual(len(validos), 2)
        self.assertEqual(invalidos, [{"linha": 4, "pedido_id": "PED-003", "erros": ["email: formato inválido"]}])


if __name__ == "__main__":
    unittest.main()
