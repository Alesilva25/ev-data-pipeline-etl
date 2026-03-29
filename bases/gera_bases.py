import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIG
# -----------------------------
N_REGISTROS = 90000
OUTPUT_DIR = "bases"

TIPOS_ESTACAO = [
    "INTERNO", "SHOPPING", "SUPERMERCADO",
    "COBERTURA", "A DEFINIR", "NOVO_TERRENO", "COMERCIAL"
]

STATUS_SISLIC = ["APROVADO", "EM ANÁLISE", "NÃO TEM LICENÇA", "PENDENTE INSTALAÇÃO"]
STATUS_INFRAGEST = ["CONECTADO", "NÃO CONECTADO", None]

STATUS_CONSOLIDADO = [
    "OPERACIONAL",
    "ESTAÇÃO EM COBERTURA",
    "SEM CONEXÃO DE REDE",
    "ALTO CUSTO - OBRAS",
    "CARREGADOR LENTO - INTERNO"
]

# -----------------------------
# HELPERS
# -----------------------------
def gerar_ids(n):
    return [f"EV-{i}" for i in range(10000, 10000 + n)]

def gerar_coordenadas(n, confiavel=False):
    if confiavel:
        return (
            np.random.uniform(-24, -23, n),  # SP latitude
            np.random.uniform(-47, -46, n)
        )
    else:
        lat = np.random.choice(
            [None, 0, *np.random.uniform(-24, -23, 10)],
            size=n
        )
        lon = np.random.choice(
            [None, 0, *np.random.uniform(-47, -46, 10)],
            size=n
        )
        return lat, lon

def random_dates(n):
    base = datetime.today()
    return [base - timedelta(days=random.randint(0, 365)) for _ in range(n)]

# -----------------------------
# BASE 1 - ATUAL
# -----------------------------
def gerar_conectados_atual(ids):
    df = pd.DataFrame({
        "ID_ESTACAO": ids,
        "STATUS E-MAIL": np.random.choice([None, "OK", "PENDENTE"], len(ids)),
        "STATUS CONSOLIDADO": np.random.choice(STATUS_CONSOLIDADO, len(ids)),
        "SISTEMA_ORIGEM": np.random.choice(["SAP", "CRM", "LEGADO"], len(ids)),
        "DATA_CARGA": random_dates(len(ids))
    })
    return df

# -----------------------------
# BASE 2 - ANTERIOR
# -----------------------------
def gerar_conectados_anterior(ids):
    ids_subset = np.random.choice(ids, int(len(ids) * 0.8), replace=False)

    lat, lon = gerar_coordenadas(len(ids_subset), confiavel=False)

    df = pd.DataFrame({
        "ID_ESTACAO": ids_subset,
        "STATUS CONSOLIDADO": np.random.choice(STATUS_CONSOLIDADO, len(ids_subset)),
        "STATUS E-MAIL": np.random.choice([None, "OK", "ERRO"], len(ids_subset)),
        "STATUS_SISLIC": np.random.choice(STATUS_SISLIC, len(ids_subset)),
        "SISTEMA_ER": np.random.choice(["CONECTADO", None], len(ids_subset)),
        "TIPO_ESTACAO_GEOPLAN": np.random.choice(TIPOS_ESTACAO + [None], len(ids_subset)),
        "TIPO_DE_PONTO 62": np.random.choice(TIPOS_ESTACAO + [None], len(ids_subset)),
        "LATITUDE": lat,
        "LONGITUDE": lon,
        "CHECKS": np.random.choice([None, "OK", "PENDENTE"], len(ids_subset)),
        "MES_REFERENCIA": np.random.choice(["01/2025", "02/2025", "03/2025"], len(ids_subset))
    })

    return df

# -----------------------------
# BASE 3 - GEOPLAN
# -----------------------------
def gerar_geoplan(ids):
    ids_subset = np.random.choice(ids, int(len(ids) * 0.7), replace=False)

    df = pd.DataFrame({
        "ID_ESTACAO": ids_subset,
        "TIPO_ESTACAO_GEOPLAN": np.random.choice(TIPOS_ESTACAO + [None], len(ids_subset))
    })

    return df

# -----------------------------
# BASE 4 - AUDIT REPORT
# -----------------------------
def gerar_audit(ids):
    ids_subset = np.random.choice(ids, int(len(ids) * 0.6), replace=False)

    lat, lon = gerar_coordenadas(len(ids_subset), confiavel=True)

    df = pd.DataFrame({
        "CODIGO_ER 1": ids_subset,
        "TIPO_DE_PONTO 62": np.random.choice(TIPOS_ESTACAO, len(ids_subset)),
        "LATITUDE 25": lat,
        "LONGITUDE 27": lon
    })

    return df

# -----------------------------
# BASE 5 - SISLIC (COM DUPLICIDADE)
# -----------------------------
def gerar_sislic(ids):
    registros = []

    for id_ in ids:
        n_linhas = np.random.choice([1, 2, 3])

        statuses = np.random.choice(STATUS_SISLIC, n_linhas)

        for s in statuses:
            registros.append({
                "CODIGO_ER": id_,
                "STATUS_SISLIC": s
            })

    return pd.DataFrame(registros)

# -----------------------------
# BASE 6 - INFRAGEST
# -----------------------------
def gerar_infratest(ids):
    ids_subset = np.random.choice(ids, int(len(ids) * 0.75), replace=False)

    df = pd.DataFrame({
        "PONTO_ER": ids_subset,
        "STATUS_INFRAGEST": np.random.choice(STATUS_INFRAGEST, len(ids_subset))
    })

    return df

# -----------------------------
# EXPORTAÇÃO
# -----------------------------
def salvar_excel(df, nome):
    path = os.path.join(OUTPUT_DIR, nome)
    df.to_excel(path, index=False)

# -----------------------------
# MAIN
# -----------------------------
def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Gerando IDs...")
    ids = gerar_ids(N_REGISTROS)

    print("Gerando bases...")

    atual = gerar_conectados_atual(ids)
    anterior = gerar_conectados_anterior(ids)
    geoplan = gerar_geoplan(ids)
    audit = gerar_audit(ids)
    sislic = gerar_sislic(ids)
    infragest = gerar_infratest(ids)

    print("Salvando arquivos...")

    salvar_excel(atual, "t_conectados_atual.xlsx")
    salvar_excel(anterior, "t_conectados_anterior.xlsx")
    salvar_excel(geoplan, "GeoPlan.xlsx")
    salvar_excel(audit, "AuditReport.xlsx")
    salvar_excel(sislic, "SisLic.xlsx")
    salvar_excel(infragest, "InfraGest.xlsx")

    print("✅ Bases geradas com sucesso!")

if __name__ == "__main__":
    main()