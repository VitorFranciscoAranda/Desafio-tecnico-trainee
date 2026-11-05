"""Testes da linha de comando (app/__main__.py)."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

from app.__main__ import main

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent

EXEMPLO = (
    "pedido_id,cliente,email,valor,data_pedido,status\n"
    "PED-001,Alfa,a@alfa.com,150.50,2026-10-29,APROVADO\n"
    "PED-002,Beta,b@beta.com,40,2026-10-30,CANCELADO\n"
    "PED-003,Gama,sem-arroba,20.00,2026-10-30,PENDENTE\n"
)

RESULTADO_ESPERADO = {
    "data_referencia": "2026-10-30",
    "total_registros": 3,
    "registros_validos": 2,
    "registros_invalidos": 1,
    "total_aprovado": "150.50",
    "invalidos": [{"linha": 4, "pedido_id": "PED-003", "erros": ["email: formato inválido"]}],
}


class BaseCli(unittest.TestCase):
    def setUp(self):
        temporaria = tempfile.TemporaryDirectory()
        self.addCleanup(temporaria.cleanup)
        self.pasta = Path(temporaria.name)
        self.entrada = self.pasta / "pedidos.csv"
        self.saida = self.pasta / "saida" / "relatorio.json"

    def executar(self, *argumentos):
        """Chama main() capturando o que seria impresso. Devolve (código, stdout, stderr)."""
        saida_padrao, saida_erro = io.StringIO(), io.StringIO()
        with redirect_stdout(saida_padrao), redirect_stderr(saida_erro):
            codigo = main(list(argumentos))
        return codigo, saida_padrao.getvalue(), saida_erro.getvalue()


class TestExecucaoCompleta(BaseCli):
    def test_t08_comando_publicado_gera_json_esperado(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
        resultado = subprocess.run(
            [sys.executable, "-m", "app", "--entrada", str(self.entrada),
            "--saida", str(self.saida), "--data-referencia", "2026-10-30"],
            cwd=RAIZ_DO_PROJETO, capture_output=True, text=True, encoding="utf-8", env=ambiente,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(json.loads(self.saida.read_text(encoding="utf-8")), RESULTADO_ESPERADO)
        self.assertIn("150.50", resultado.stdout)
        self.assertIn(str(self.saida), resultado.stdout)

    def test_sem_data_de_referencia_usa_hoje(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        codigo, _, _ = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida))
        self.assertEqual(codigo, 0)
        relatorio = json.loads(self.saida.read_text(encoding="utf-8"))
        self.assertEqual(relatorio["data_referencia"], date.today().isoformat())

    def test_t06_somente_cabecalho(self):
        self.entrada.write_text("pedido_id,cliente,email,valor,data_pedido,status\n", encoding="utf-8")
        codigo, _, _ = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida),
                                    "--data-referencia", "2026-10-30")
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(self.saida.read_text(encoding="utf-8")), {
            "data_referencia": "2026-10-30",
            "total_registros": 0,
            "registros_validos": 0,
            "registros_invalidos": 0,
            "total_aprovado": "0.00",
            "invalidos": [],
        })

    def test_t05_aprovado_invalido_fica_fora_da_soma(self):
        self.entrada.write_text(
            "pedido_id,cliente,email,valor,data_pedido,status\n"
            "A,Alfa,a@alfa.com,10.00,2026-10-29, aprovado \n"   # válido e aprovado: entra
            "B,Beta,b@beta.com,20.00,2026-10-29,PENDENTE\n"      # pendente: fica fora
            "C,Gama,c@gama.com,30.00,2026-10-29,CANCELADO\n"     # cancelado: fica fora
            "D,Delta,sem-arroba,999.00,2026-10-29,APROVADO\n",   # aprovado, mas inválido: fica fora
            encoding="utf-8",
        )
        codigo, _, _ = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida),
                                    "--data-referencia", "2026-10-30")
        relatorio = json.loads(self.saida.read_text(encoding="utf-8"))
        self.assertEqual(codigo, 0)
        self.assertEqual(relatorio["total_aprovado"], "10.00")
        self.assertEqual(relatorio["registros_validos"], 3)
        self.assertEqual(relatorio["registros_invalidos"], 1)

    def test_relatorio_de_demonstracao_entregue_esta_atualizado(self):
        # Gera de novo o relatório da demonstração e compara com o que foi entregue em saida/.
        entregue = RAIZ_DO_PROJETO / "saida" / "relatorio_demonstracao.json"
        codigo, _, _ = self.executar("--entrada", str(RAIZ_DO_PROJETO / "dados" / "pedidos_demonstracao.csv"),
                                    "--saida", str(self.saida), "--data-referencia", "2026-10-30")
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(self.saida.read_text(encoding="utf-8")),
                        json.loads(entregue.read_text(encoding="utf-8")))

    def test_entrada_nao_e_modificada(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        antes = self.entrada.read_bytes()
        self.executar("--entrada", str(self.entrada), "--saida", str(self.saida), "--data-referencia", "2026-10-30")
        self.assertEqual(self.entrada.read_bytes(), antes)


class TestFalhasControladas(BaseCli):
    def test_t07_arquivo_inexistente(self):
        codigo, saida, erro = self.executar("--entrada", str(self.pasta / "nao_existe.csv"), "--saida", str(self.saida))
        self.assertNotEqual(codigo, 0)
        self.assertIn("não encontrado", erro)
        self.assertNotIn("Traceback", erro)
        self.assertEqual(saida, "")
        self.assertFalse(self.saida.exists())

    def test_t07_coluna_obrigatoria_ausente(self):
        self.entrada.write_text("pedido_id,cliente,valor,data_pedido,status\n", encoding="utf-8")
        codigo, _, erro = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida))
        self.assertNotEqual(codigo, 0)
        self.assertIn("email", erro)
        self.assertFalse(self.saida.exists())

    def test_t09_codificacao_invalida(self):
        self.entrada.write_bytes(EXEMPLO.replace("Alfa", "João").encode("latin-1"))
        codigo, _, erro = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida))
        self.assertNotEqual(codigo, 0)
        self.assertIn("UTF-8", erro)
        self.assertFalse(self.saida.exists())

    def test_t10_entrada_igual_a_saida(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        antes = self.entrada.read_bytes()
        codigo, _, erro = self.executar("--entrada", str(self.entrada), "--saida", str(self.entrada))
        self.assertNotEqual(codigo, 0)
        self.assertIn("mesmo arquivo", erro)
        self.assertEqual(self.entrada.read_bytes(), antes)

    def test_t10_mesmo_arquivo_escrito_de_outro_jeito(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        self.saida.parent.mkdir()
        outro_caminho = self.pasta / "saida" / ".." / "pedidos.csv"
        codigo, _, _ = self.executar("--entrada", str(self.entrada), "--saida", str(outro_caminho))
        self.assertNotEqual(codigo, 0)
        self.assertEqual(self.entrada.read_text(encoding="utf-8"), EXEMPLO)

    def test_falha_avisa_que_relatorio_antigo_nao_vale(self):
        self.saida.parent.mkdir()
        self.saida.write_text("{}", encoding="utf-8")
        codigo, _, erro = self.executar("--entrada", str(self.pasta / "nao_existe.csv"), "--saida", str(self.saida))
        self.assertNotEqual(codigo, 0)
        self.assertIn("execução anterior", erro)

    def test_falha_ao_gravar(self):
        self.entrada.write_text(EXEMPLO, encoding="utf-8")
        self.saida.mkdir(parents=True)  # a saída é uma pasta: não dá para gravar
        codigo, _, erro = self.executar("--entrada", str(self.entrada), "--saida", str(self.saida))
        self.assertNotEqual(codigo, 0)
        self.assertIn("não foi possível gravar", erro)


class TestArgumentos(BaseCli):
    def test_help(self):
        with self.assertRaises(SystemExit) as contexto:
            self.executar("--help")
        self.assertEqual(contexto.exception.code, 0)

    def test_saida_obrigatoria(self):
        with self.assertRaises(SystemExit) as contexto:
            self.executar("--entrada", str(self.entrada))
        self.assertNotEqual(contexto.exception.code, 0)

    def test_data_de_referencia_invalida(self):
        for data_texto in ["2026-02-30", "30/10/2026", "20261030"]:
            with self.subTest(data=data_texto):
                with self.assertRaises(SystemExit) as contexto:
                    self.executar("--entrada", str(self.entrada), "--saida", str(self.saida),
                                "--data-referencia", data_texto)
                self.assertNotEqual(contexto.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
