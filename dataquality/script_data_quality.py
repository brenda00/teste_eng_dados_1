from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, current_date

spark = SparkSession.builder \
    .appName("Data Quality") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .getOrCreate()

hadoop_conf = spark._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", "")
hadoop_conf.set("fs.s3a.secret.key", "")
hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")
hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# Ler CSV do S3
df_silver = spark.read.csv("s3a://bucket-silveer/tb_cliente", header=True, inferSchema=True)

# ------------------------------
# Dimensão: COMPLETUDE
# Verifica se campos obrigatórios estão preenchidos (não nulos ou vazios).
# ------------------------------
campos_obrigatorios = ["cod_cliente", "nm_cliente", "dt_nascimento_cliente", "dt_atualizacao", "vl_renda"]
completude_resultados = {}
for campo in campos_obrigatorios:
    nulos = df_silver.filter(col(campo).isNull()).count()
    completude_resultados[campo] = nulos

print(completude_resultados)

# ------------------------------
# Dimensão: UNICIDADE
# Compara a contagem total de registros com a contagem de cod_cliente distintos.
# ------------------------------
total_registros = df_silver.count()
distinct_clientes = df_silver.select("cod_cliente").distinct().count()
unicidade_valida = (total_registros == distinct_clientes)

print(f"Total registros: {total_registros}")
print(f"Distintos cod_cliente: {distinct_clientes}")
print(f"Unicidade válida? {'Sim' if unicidade_valida else 'Não'}")

# ------------------------------
# Dimensão: ACURÁCIA (formato de telefone)
# Valida se o campo num_telefone_cliente segue o padrão esperado: (NN)NNNNN-NNNN
# ------------------------------
regex_telefone = r"^\(\d{2}\)\d{5}-\d{4}$"
invalidos_telefone = df_silver.filter(~col("num_telefone_cliente").rlike(regex_telefone) & col("num_telefone_cliente").isNotNull()).count()

print(f"Telefones fora do padrão: {invalidos_telefone}")

# ------------------------------
# Dimensão: CONSISTÊNCIA (renda positiva)
# Verifica se a coluna vl_renda contém valores maiores ou iguais a zero.
# ------------------------------
renda_invalida = df_silver.filter(col("vl_renda") < 0).count()

print(f"Registros com renda negativa: {renda_invalida}")

# ------------------------------
# Dimensão: VALIDADE
# Verifica se a data de nascimento (dt_nascimento_cliente) não está no futuro.
# Verifica nomes vazios ou apenas com espaços
# Nomes com um único caractere repetido
# ------------------------------
datas_invalidas = df_silver.filter(col("dt_nascimento_cliente") > current_date()).count()
print(f"Datas de nascimento futuras: {datas_invalidas}")

nome_vazio = df_silver.filter((col("nm_cliente").isNull()) | (regexp_replace(col("nm_cliente"), "[\\s\\t]", "") == "")).count()
print(f"Nomes vazios ou com apenas espaços/tabulações: {nome_vazio}")