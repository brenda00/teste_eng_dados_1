from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
from pyspark.sql.functions import col, upper, when, row_number, lit
from pyspark.sql.window import Window
import datetime

def create_spark_session():
    spark = SparkSession.builder.getOrCreate()
    return spark

def process_client_data(spark, input_path, bronze_path, silver_path):
    schema = StructType([
        StructField("cod_cliente", IntegerType(), True),
        StructField("nm_cliente", StringType(), True),
        StructField("nm_pais_cliente", StringType(), True),
        StructField("nm_cidade_cliente", StringType(), True),
        StructField("nm_rua_cliente", StringType(), True),
        StructField("num_casa_cliente", IntegerType(), True),
        StructField("telefone_cliente", IntegerType(), True),
        StructField("dt_nascimento_cliente", DateType(), True),
        StructField("dt_atualizacao", DateType(), True),
        StructField("tp_pessoa", StringType(), True),
        StructField("vl_renda", DoubleType(), True)
    ])

    df = spark.read \
        .option("header", True) \
        .schema(schema) \
        .csv(input_path)

    #Cria coluna de partição lógica
    data_proc = datetime.datetime.today().strftime("%Y%m%d")
    df = df.withColumn("anomesdia", lit(data_proc))

    df_bronze = df \
        .withColumn("nm_cliente", upper(col("nm_cliente"))) \
        .withColumnRenamed("telefone_cliente", "num_telefone_cliente")

    print("camada bronze com telefone modificado")
    df_bronze.show(10)

    df_bronze.write \
        .mode("overwrite") \
        .partitionBy("anomesdia") \
        .option("compression", "snappy") \
        .format("parquet") \
        .save(bronze_path)
    
    print("Salvar arquivo na camada bronze")

    #Deduplicação para a camada Silver
    window_spec = Window.partitionBy("cod_cliente").orderBy(col("dt_atualizacao").desc())
    df_silver = df_bronze \
    .withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")

    df_silver = df_silver.withColumn(
        "num_telefone_cliente",
        when(
            col("num_telefone_cliente").rlike(r"^\(\d{2}\)\d{5}-\d{4}$"),
            col("num_telefone_cliente")
        ).otherwise(None)
    )

    df_silver.write \
        .mode("overwrite") \
        .partitionBy("anomesdia") \
        .option("compression", "snappy") \
        .format("parquet") \
        .save(silver_path)

def main():
    spark = create_spark_session()
    input_path =  "s3://etlproj-landing-zone/arquivo/clientes_sinteticos.csv"
    bronze_path = "s3a://etlproj-bronze/tabela_cliente_landing"
    silver_path = "s3a://etlproj-silver/tb_cliente"

    process_client_data(spark, input_path, bronze_path, silver_path)

if __name__ == "__main__":
    main()    