"""Teste inicial: garante a versão mínima do Python."""

import sys
import unittest


class TestAmbiente(unittest.TestCase):
    def test_versao_do_python(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))


if __name__ == "__main__":
    unittest.main()
