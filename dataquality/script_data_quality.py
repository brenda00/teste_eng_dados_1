from pyspark.sql import SparkSession
from pyspark.sql.functions import col,  regexp_replace,  current_date, length


def create_spark_session():
    spark = SparkSession.builder.getOrCreate()
    return spark

def run_data_quality(spark, path_silver):


    df_silver = spark.read.format("parquet").load(path_silver)

    # ------------------------------
    # COMPLETUDE
    campos_obrigatorios = ["cod_cliente", "nm_cliente", "dt_nascimento_cliente", "dt_atualizacao", "vl_renda"]
    print("\n🔎 Validação de COMPLETUDE:")
    for campo in campos_obrigatorios:
        nulos = df_silver.filter(col(campo).isNull()).count()
        print(f"- {campo}: {nulos} valores nulos")

    # ------------------------------
    # UNICIDADE
    total = df_silver.count()
    distintos = df_silver.select("cod_cliente").distinct().count()
    print("\n🔎 Validação de UNICIDADE:")
    print(f"- Total registros: {total}")
    print(f"- Distintos cod_cliente: {distintos}")
    print(f"- Unicidade válida? {'Sim' if total == distintos else 'Não'}")

    # ------------------------------
    # ACURÁCIA - formato telefone
    print("\n🔎 Validação de ACURÁCIA (telefone):")
    regex_tel = r"^\(\d{2}\)\d{5}-\d{4}$"
    invalidos = df_silver.filter(~col("num_telefone_cliente").rlike(regex_tel) & col("num_telefone_cliente").isNotNull()).count()
    print(f"- Telefones inválidos: {invalidos}")

    # ------------------------------
    # CONSISTÊNCIA - renda positiva
    print("\n🔎 Validação de CONSISTÊNCIA (renda):")
    renda_negativa = df_silver.filter(col("vl_renda") < 0).count()
    print(f"- Registros com renda negativa: {renda_negativa}")

    # ------------------------------
    # VALIDADE - datas e nomes
    print("\n🔎 Validação de VALIDADE:")
    data_futura = df_silver.filter(col("dt_nascimento_cliente") > current_date()).count()
    print(f"- Datas de nascimento futuras: {data_futura}")

    nome_vazio = df_silver.filter(
        (col("nm_cliente").isNull()) | 
        (regexp_replace(col("nm_cliente"), "[\\s\\t]", "") == "") |
        (length(col("nm_cliente")) == 1) |
        (col("nm_cliente").rlike(r"^(.)\1+$"))  # Ex: "AAAA" ou "1111"
    ).count()

    print(f"- Nomes inválidos (vazio, repetido ou um caractere): {nome_vazio}")

def main():
    spark = create_spark_session()
    path_silver = "s3a://etlproj-silver/tb_cliente/"
    run_data_quality(spark, path_silver)

if __name__ == "__main__":
    main()