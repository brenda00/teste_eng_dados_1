import unittest
import re

# ========================
# Função a ser testada
# ========================
def validar_telefone(telefone: str) -> bool:
    """
    Valida se o telefone está no formato (NN)NNNNN-NNNN
    """
    if telefone is None:
        return False
    padrao = r"^\(\d{2}\)\d{5}-\d{4}$"
    return bool(re.match(padrao, telefone))

# ========================
# Testes unitários
# ========================
class TestValidarTelefone(unittest.TestCase):

    def test_happy_path(self):
        self.assertTrue(validar_telefone("(11)91234-5678"))

    def test_formatacao_errada(self):
        self.assertFalse(validar_telefone("11-91234-5678"))
        self.assertFalse(validar_telefone("11912345678"))
        self.assertFalse(validar_telefone(""))

    def test_borda_caracteres(self):
        self.assertFalse(validar_telefone("(1)12345-6789"))   # DDD com 1 dígito
        self.assertFalse(validar_telefone("(111)12345-6789")) # DDD com 3 dígitos

    def test_nulo(self):
        self.assertFalse(validar_telefone(None))

    def test_caracteres_invalidos(self):
        self.assertFalse(validar_telefone("(11)ABCDE-FGHI"))
        self.assertFalse(validar_telefone("(11)9123A-5678"))

# ========================
# Execução e resultado
# ========================
if __name__ == '__main__':
    # Execução dos testes + escrita do resultado
    with open("../testeunitario/resultados.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner, exit=False)
