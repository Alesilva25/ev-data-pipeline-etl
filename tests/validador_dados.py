import pandas as pd

# -----------------------------
# VALIDAÇÕES INDIVIDUAIS
# -----------------------------

def validar_nulos(df, coluna):
    assert df[coluna].isna().sum() > 0, f"❌ Coluna {coluna} não possui valores nulos"


def validar_divergencia(df, col1, col2):
    divergentes = (df[col1] != df[col2]) & df[col1].notna() & df[col2].notna()
    assert divergentes.sum() > 0, f"❌ Não há divergência entre {col1} e {col2}"


def validar_valor_especifico(df, coluna, valor):
    assert (df[coluna] == valor).sum() > 0, f"❌ Não existe valor '{valor}' em {coluna}"


def validar_coordenadas_invalidas(df):
    cond = (df["LATITUDE"].isna()) | (df["LATITUDE"] == 0)
    assert cond.sum() > 0, "❌ Não há coordenadas inválidas para teste"


def validar_sislic_multiplas_linhas(df):
    counts = df.groupby("CODIGO_ER").size()
    assert (counts > 1).sum() > 0, "❌ Nenhum ER com múltiplas linhas no SisLic"


def validar_sislic_aprovado(df):
    assert (df["STATUS_SISLIC"] == "APROVADO").sum() > 0, "❌ Não há status APROVADO"


def validar_infragest_cenarios(df):
    assert df["STATUS_INFRAGEST"].isna().sum() > 0, "❌ Falta cenário vazio InfraGest"
    assert (df["STATUS_INFRAGEST"] == "CONECTADO").sum() > 0, "❌ Falta CONECTADO"
    assert (df["STATUS_INFRAGEST"] == "NÃO CONECTADO").sum() > 0, "❌ Falta NÃO CONECTADO"


# -----------------------------
# VALIDADOR PRINCIPAL
# -----------------------------

def validar_dados(
    conectados_atual,
    conectados_anterior,
    geoplan,
    audit,
    sislic,
    infragest
):
    print("🔍 Iniciando validações...\n")

    # --- Conectados anterior
    validar_nulos(conectados_anterior, "TIPO_ESTACAO_GEOPLAN")
    validar_coordenadas_invalidas(conectados_anterior)

    # --- Divergência entre bases
    merged = conectados_anterior.merge(
        geoplan,
        on="ID_ESTACAO",
        how="inner",
        suffixes=("", "_AUX")
    )

    validar_divergencia(
        merged,
        "TIPO_ESTACAO_GEOPLAN",
        "TIPO_ESTACAO_GEOPLAN_AUX"
    )

    # --- GeoPlan
    validar_valor_especifico(geoplan, "TIPO_ESTACAO_GEOPLAN", "A DEFINIR")

    # --- Audit
    validar_valor_especifico(audit, "TIPO_DE_PONTO 62", "INTERNO")

    # --- SisLic
    validar_sislic_multiplas_linhas(sislic)
    validar_sislic_aprovado(sislic)

    # --- InfraGest
    validar_infragest_cenarios(infragest)

    print("\n✅ Todas as validações passaram com sucesso!")

if __name__ == "__main__":
    conectados_atual = pd.read_excel(r"bases\t_conectados_atual.xlsx")
    conectados_anterior = pd.read_excel(r"bases\t_conectados_anterior.xlsx")
    geoplan = pd.read_excel(r"bases\GeoPlan.xlsx")
    audit = pd.read_excel(r"bases\AuditReport.xlsx")
    sislic = pd.read_excel(r"bases\SisLic.xlsx")
    infragest = pd.read_excel(r"bases\InfraGest.xlsx")
                              
    validar_dados(conectados_atual, conectados_anterior, geoplan, audit, sislic, infragest)