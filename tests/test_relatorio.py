"""Testes do módulo app.relatorio."""

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.relatorio import ErroGravacao, gravar_relatorio, montar_relatorio, total_aprovado

REFERENCIA = date(2026, 10, 30)


def pedido(valor, status):
    """Pedido válido mínimo: para a soma só importam valor e status."""
    return {"valor": valor, "status": status}


class TestTotalAprovado(unittest.TestCase):
    def test_t05_soma_somente_aprovados(self):
        validos = [pedido("100.00", "APROVADO"), pedido("50", "PENDENTE"), pedido("30", "CANCELADO"), pedido("0.5", "APROVADO")]
        self.assertEqual(total_aprovado(validos), "100.50")

    def test_t05_sem_erro_de_arredondamento(self):
        # Com float, 0.1 + 0.2 daria 0.30000000000000004.
        validos = [pedido("0.10", "APROVADO"), pedido("0.20", "APROVADO")]
        self.assertEqual(total_aprovado(validos), "0.30")

    def test_sem_aprovados_da_zero_com_duas_casas(self):
        self.assertEqual(total_aprovado([]), "0.00")
        self.assertEqual(total_aprovado([pedido("10", "PENDENTE")]), "0.00")

    def test_valor_inteiro_sai_com_duas_casas(self):
        self.assertEqual(total_aprovado([pedido("40", "APROVADO")]), "40.00")


class TestMontarRelatorio(unittest.TestCase):
    def test_t05_invalidos_ficam_fora_da_soma(self):
        validos = [pedido("10", "APROVADO")]
        invalidos = [{"linha": 3, "pedido_id": "PED-002", "erros": ["email: formato inválido"]}]
        relatorio = montar_relatorio(validos, invalidos, REFERENCIA)
        self.assertEqual(relatorio["total_aprovado"], "10.00")

    def test_contagens_e_data(self):
        validos = [pedido("10", "APROVADO"), pedido("20", "PENDENTE")]
        invalidos = [{"linha": 4, "pedido_id": "X", "erros": ["valor: obrigatório"]}]
        relatorio = montar_relatorio(validos, invalidos, REFERENCIA)
        self.assertEqual(relatorio["data_referencia"], "2026-10-30")
        self.assertEqual(relatorio["total_registros"], 3)
        self.assertEqual(relatorio["registros_validos"], 2)
        self.assertEqual(relatorio["registros_invalidos"], 1)
        self.assertEqual(relatorio["invalidos"], invalidos)

    def test_t06_sem_registros(self):
        relatorio = montar_relatorio([], [], REFERENCIA)
        self.assertEqual(relatorio, {
            "data_referencia": "2026-10-30",
            "total_registros": 0,
            "registros_validos": 0,
            "registros_invalidos": 0,
            "total_aprovado": "0.00",
            "invalidos": [],
        })


class TestGravarRelatorio(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.relatorio = montar_relatorio([], [{"linha": 2, "pedido_id": "PED-1", "erros": ["cliente: obrigatório"]}], REFERENCIA)

    def test_grava_json_utf8_e_cria_pasta(self):
        caminho = Path(self.pasta.name) / "nova" / "pasta" / "relatorio.json"
        gravar_relatorio(self.relatorio, caminho)
        conteudo = caminho.read_text(encoding="utf-8")
        self.assertIn("obrigatório", conteudo)  # acento gravado direto, sem ó
        self.assertEqual(json.loads(conteudo), self.relatorio)
        self.assertFalse(caminho.with_name("relatorio.json.tmp").exists())

    def test_substitui_relatorio_anterior(self):
        caminho = Path(self.pasta.name) / "relatorio.json"
        caminho.write_text("antigo", encoding="utf-8")
        gravar_relatorio(self.relatorio, caminho)
        self.assertEqual(json.loads(caminho.read_text(encoding="utf-8")), self.relatorio)

    def test_falha_de_gravacao_gera_erro_controlado(self):
        caminho = Path(self.pasta.name) / "uma_pasta"
        caminho.mkdir()  # o destino é uma pasta, então não dá para gravar o arquivo
        with self.assertRaises(ErroGravacao):
            gravar_relatorio(self.relatorio, caminho)
        self.assertFalse(caminho.with_name("uma_pasta.tmp").exists())


if __name__ == "__main__":
    unittest.main()
