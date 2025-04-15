from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, floor, datediff, current_date
import jdk
import os

java_home = jdk.install("17")
os.environ["JAVA_HOME"] = java_home

spark = SparkSession.builder.appName("Análise de Clientes").getOrCreate()

df = spark.read.option("header", True).csv("../datasets/clientes_sinteticos.csv")

# Top 5 clientes com mais atualizações (por cod_cliente)
top_clientes = df.groupBy("cod_cliente").count().orderBy("count", ascending=False).limit(5)
print("Top 5 clientes com mais atualizações:")
top_clientes.show()


#2. Média de idade dos clientes (considera a data de nascimento válida)
df_idade = df.filter(col("dt_nascimento_cliente").isNotNull()) \
    .withColumn("idade", floor(datediff(current_date(), col("dt_nascimento_cliente")) / 365.25))

media_idade_df = df_idade.agg(avg("idade").alias("media_idade"))

print("Média de idade dos clientes:")
media_idade_df.show()