import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import sys
import io

# Função a ser testada
def validar_telefone(df):
    return df.withColumn(
        "telefone_valido",
        when(col("num_telefone_cliente").rlike(r"^\(\d{2}\)\d{5}-\d{4}$"), True).otherwise(False)
    )

# Classe de testes
class TestValidacaoTelefone(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder \
            .appName("Teste Unitário - Telefone") \
            .master("local[*]") \
            .getOrCreate()

        cls.schema = ["cod_cliente", "num_telefone_cliente"]

    def test_telefone_valido(self):
        dados = [("1", "(11)91234-5678"), ("2", "(99)98765-4321")]
        df = self.spark.createDataFrame(dados, self.schema)
        resultado = validar_telefone(df)
        valores = resultado.select("telefone_valido").rdd.flatMap(lambda x: x).collect()
        self.assertTrue(all(valores))  # todos devem ser True

    def test_telefone_invalido(self):
        dados = [("1", "11912345678"), ("2", "abcd")]
        df = self.spark.createDataFrame(dados, self.schema)
        resultado = validar_telefone(df)
        valores = resultado.select("telefone_valido").rdd.flatMap(lambda x: x).collect()
        self.assertTrue(all([not x for x in valores]))  # todos devem ser False

    def test_telefone_nulo_ou_vazio(self):
        dados = [("1", None), ("2", ""), ("3", " ")]
        df = self.spark.createDataFrame(dados, self.schema)
        resultado = validar_telefone(df)
        valores = resultado.select("telefone_valido").rdd.flatMap(lambda x: x).collect()
        self.assertTrue(all([not x for x in valores]))  # todos devem ser False

# Execução dos testes (se estiver rodando como script)

if __name__ == "__main__":
    # Redireciona stdout para capturar o resultado
    resultado_buffer = io.StringIO()
    runner = unittest.TextTestRunner(stream=resultado_buffer, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestValidacaoTelefone)
    runner.run(suite)

    # Salva em arquivo
    with open("/testeunitario/resultados.txt", "w", encoding="utf-8") as f:
        f.write(resultado_buffer.getvalue())

    # Também imprime no terminal
    print(resultado_buffer.getvalue())
