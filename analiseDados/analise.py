from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
from pyspark.sql.functions import col, count, floor, avg, datediff, current_date

def create_spark_session():
    spark = SparkSession.builder \
        .appName("Análise de Clientes") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .getOrCreate()

    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", "")
    hadoop_conf.set("fs.s3a.secret.key", "")
    hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    return spark

def analisar_clientes(spark, input_path):

    # Leitura do CSV diretamente da landing zone
    df = spark.read.option("header", True).csv(input_path)

    print("✅ Total de registros carregados:", df.count())

    # --------------------------------------------
    # 1. Top 5 clientes com mais atualizações
    # --------------------------------------------
    print("\n Top 5 clientes com mais atualizações:")
    top_clientes = df.groupBy("cod_cliente").agg(count("*").alias("total_atualizacoes")) \
        .orderBy(col("total_atualizacoes").desc()) \
        .limit(5)

    top_clientes.show(truncate=False)

    # --------------------------------------------
    # 2. Média de idade dos clientes
    # --------------------------------------------
    print("\n Média de idade dos clientes:")
    df_idade = df.filter(col("dt_nascimento_cliente").isNotNull()) \
        .withColumn("idade", floor(datediff(current_date(), col("dt_nascimento_cliente")) / 365.25))

    media_idade = df_idade.agg(avg("idade").alias("media_idade"))
    media_idade.show()

def main():
    spark = create_spark_session()
    input_path = "s3://etlproj-landing-zone/arquivo/clientes_sinteticos.csv"
    analisar_clientes(spark, input_path)

if __name__ == "__main__":
    main()
