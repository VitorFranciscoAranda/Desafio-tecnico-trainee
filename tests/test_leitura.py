"""Testes do módulo app.leitura."""

import tempfile
import unittest
from pathlib import Path

from app.leitura import ErroEstrutural, ler_pedidos, validar_cabecalho

CABECALHO = "pedido_id,cliente,email,valor,data_pedido,status\n"


class TestValidarCabecalho(unittest.TestCase):
    def test_aceita_ordem_diferente_e_coluna_extra(self):
        cabecalho = ["status", "valor", "pedido_id", "observacao", "email", "cliente", "data_pedido"]
        validar_cabecalho(cabecalho)  # não deve lançar erro

    def test_coluna_obrigatoria_ausente(self):
        cabecalho = ["pedido_id", "cliente", "valor", "data_pedido", "status"]
        with self.assertRaises(ErroEstrutural) as contexto:
            validar_cabecalho(cabecalho)
        self.assertIn("email", str(contexto.exception))

    def test_coluna_duplicada(self):
        cabecalho = ["pedido_id", "cliente", "email", "valor", "data_pedido", "status", "email"]
        with self.assertRaises(ErroEstrutural) as contexto:
            validar_cabecalho(cabecalho)
        self.assertIn("duplicadas", str(contexto.exception))

    def test_nome_de_coluna_diferencia_maiusculas(self):
        cabecalho = ["Pedido_ID", "cliente", "email", "valor", "data_pedido", "status"]
        with self.assertRaises(ErroEstrutural):
            validar_cabecalho(cabecalho)


class TestLerPedidos(unittest.TestCase):
    def setUp(self):
        # Cria uma pasta temporária nova para cada teste; ela é apagada no final.
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)

    def criar_csv(self, conteudo):
        """Grava os bytes em um arquivo temporário e devolve o caminho."""
        caminho = Path(self.pasta.name) / "pedidos.csv"
        caminho.write_bytes(conteudo)
        return caminho

    def test_le_registros_com_numero_da_linha(self):
        texto = CABECALHO + "PED-001,Alfa,a@alfa.com,150.50,2026-10-29,APROVADO\n\nPED-002,Beta,b@beta.com,40,2026-10-30,CANCELADO\n"
        registros = ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertEqual(len(registros), 2)
        self.assertEqual(registros[0]["pedido_id"], "PED-001")
        self.assertEqual(registros[0]["linha"], 2)
        self.assertEqual(registros[1]["linha"], 4)  # a linha 3 em branco foi pulada

    def test_ordem_diferente_e_coluna_extra(self):
        texto = "status,obs,pedido_id,cliente,email,valor,data_pedido\nAPROVADO,xyz,PED-001,Alfa,a@alfa.com,10,2026-10-29\n"
        registros = ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertEqual(registros[0]["status"], "APROVADO")
        self.assertEqual(registros[0]["pedido_id"], "PED-001")
        self.assertNotIn("obs", registros[0])

    def test_campo_entre_aspas_com_virgula(self):
        texto = CABECALHO + 'PED-001,"Silva, Ana",a@alfa.com,10,2026-10-29,APROVADO\n'
        registros = ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertEqual(registros[0]["cliente"], "Silva, Ana")

    def test_linha_so_com_separadores_vira_registro(self):
        texto = CABECALHO + ",,,,,\n"
        registros = ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["pedido_id"], "")

    def test_linha_com_espacos_e_ignorada(self):
        texto = CABECALHO + "   \n"
        self.assertEqual(ler_pedidos(self.criar_csv(texto.encode("utf-8"))), [])

    def test_somente_cabecalho_tem_zero_registros(self):
        self.assertEqual(ler_pedidos(self.criar_csv(CABECALHO.encode("utf-8"))), [])

    def test_aceita_bom_do_excel(self):
        texto = CABECALHO + "PED-001,Alfa,a@alfa.com,10,2026-10-29,APROVADO\n"
        registros = ler_pedidos(self.criar_csv(b"\xef\xbb\xbf" + texto.encode("utf-8")))
        self.assertEqual(registros[0]["pedido_id"], "PED-001")

    def test_arquivo_vazio(self):
        with self.assertRaises(ErroEstrutural) as contexto:
            ler_pedidos(self.criar_csv(b""))
        self.assertIn("vazio", str(contexto.exception))

    def test_arquivo_inexistente(self):
        with self.assertRaises(ErroEstrutural) as contexto:
            ler_pedidos(Path(self.pasta.name) / "nao_existe.csv")
        self.assertIn("não encontrado", str(contexto.exception))

    def test_quantidade_de_campos_diferente(self):
        texto = CABECALHO + "PED-001,Alfa,a@alfa.com,10,2026-10-29\n"
        with self.assertRaises(ErroEstrutural) as contexto:
            ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertIn("linha 2", str(contexto.exception))

    def test_codificacao_invalida(self):
        texto = CABECALHO + "PED-001,João,a@alfa.com,10,2026-10-29,APROVADO\n"
        with self.assertRaises(ErroEstrutural) as contexto:
            ler_pedidos(self.criar_csv(texto.encode("latin-1")))
        self.assertIn("UTF-8", str(contexto.exception))

    def test_csv_malformado(self):
        texto = CABECALHO + 'PED-001,"Alfa"x,a@alfa.com,10,2026-10-29,APROVADO\n'
        with self.assertRaises(ErroEstrutural) as contexto:
            ler_pedidos(self.criar_csv(texto.encode("utf-8")))
        self.assertIn("malformado", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
