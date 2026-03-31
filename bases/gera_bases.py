import pandas as pd
import numpy as np
import os

# -------------------------
# CONFIG
# -------------------------
N = 50000
np.random.seed(42)

IDS = [f"EV-{i}" for i in np.random.choice(range(10000, 99999), N, replace=False)]

STATUS_CONSOLIDADO = ["OPERACIONAL", "COBERTURA", "QUEBRA", None]
STATUS_EMAIL = ["ENVIADO", "PENDENTE", None]
SISTEMA_ORIGEM = ["SAP", "API", "MANUAL"]

TIPO_GEOPLAN = [
    "INTERNO", "SHOPPING", "SUPERMERCADO", "COBERTURA",
    "A DEFINIR", "NOVO_TERRENO", "COMERCIAL", None
]

STATUS_CONEXAO = ["CONECTADO", "NÃO CONECTADO", None]

# -------------------------
# BASE 1 - ATUAL
# -------------------------
def gerar_conectados_atual():
    df = pd.DataFrame({
        "ID_ESTACAO": IDS,
        "STATUS_EMAIL": np.random.choice(STATUS_EMAIL, N),
        "STATUS_CONSOLIDADO": np.random.choice(STATUS_CONSOLIDADO, N),
        "SISTEMA_ORIGEM": np.random.choice(SISTEMA_ORIGEM, N),
        "DATA_CARGA": pd.to_datetime("2025-01-01") + pd.to_timedelta(np.random.randint(0, 30, N), unit='d')
    })
    return df

# -------------------------
# BASE 2 - ANTERIOR
# -------------------------
def gerar_conectados_anterior():
    sample_ids = np.random.choice(IDS, int(N * 0.8), replace=False)

    df = pd.DataFrame({
        "ID_ESTACAO": sample_ids,
        "STATUS_CONSOLIDADO": np.random.choice(STATUS_CONSOLIDADO, len(sample_ids)),
        "STATUS_EMAIL": np.random.choice(STATUS_EMAIL, len(sample_ids)),
        "STATUS_SISLIC": np.random.choice(["APROVADO", "EM ANÁLISE", None], len(sample_ids)),
        "SISTEMA_ER": np.random.choice(STATUS_CONEXAO, len(sample_ids)),
        "TIPO_ESTACAO_GEOPLAN": np.random.choice(TIPO_GEOPLAN, len(sample_ids)),
        "TIPO_DE_PONTO 62": np.random.choice(["RÁPIDO", "LENTO", None], len(sample_ids)),
        "LATITUDE": np.random.uniform(-30, -10, len(sample_ids)),
        "LONGITUDE": np.random.uniform(-60, -40, len(sample_ids)),
        "CHECKS": np.random.randint(0, 5, len(sample_ids)),
        "MES_REFERENCIA": np.random.choice(["2025-01", "2025-02", None], len(sample_ids))
    })

    # Inserir nulos
    for col in ["LATITUDE", "LONGITUDE", "TIPO_ESTACAO_GEOPLAN"]:
        df.loc[df.sample(frac=0.1).index, col] = None

    return df

# -------------------------
# BASE 3 - GEOPLAN
# -------------------------
def gerar_geoplan():
    ids = np.random.choice(IDS, int(N * 0.7), replace=False)
    return pd.DataFrame({
        "ID_ESTACAO": ids,
        "TIPO_ESTACAO_GEOPLAN": np.random.choice(TIPO_GEOPLAN, len(ids))
    })

# -------------------------
# BASE 4 - AUDIT
# -------------------------
def gerar_audit():
    ids = np.random.choice(IDS, int(N * 0.75), replace=False)

    df = pd.DataFrame({
        "CODIGO_ER 1": ids,
        "TIPO_DE_PONTO 62": np.random.choice(["RÁPIDO", "LENTO"], len(ids)),
        "LATITUDE 25": np.random.uniform(-30, -10, len(ids)),
        "LONGITUDE 27": np.random.uniform(-60, -40, len(ids))
    })

    # Parte divergente
    df.loc[df.sample(frac=0.2).index, "LATITUDE 25"] += np.random.uniform(0.01, 0.5)

    return df

# -------------------------
# BASE 5 - SISLIC
# -------------------------
def gerar_sislic():
    rows = []

    for id_ in np.random.choice(IDS, int(N * 0.6), replace=False):
        n = np.random.randint(1, 4)
        for _ in range(n):
            rows.append({
                "CODIGO_ER": id_,
                "STATUS_SISLIC": np.random.choice(["APROVADO", "EM ANÁLISE", "REPROVADO"])
            })

    return pd.DataFrame(rows)

# -------------------------
# BASE 6 - INFRAGEST
# -------------------------
def gerar_infrgest():
    ids = np.random.choice(IDS, int(N * 0.85), replace=False)

    return pd.DataFrame({
        "PONTO_ER": ids,
        "STATUS_INFRAGEST": np.random.choice(STATUS_CONEXAO, len(ids))
    })

# -------------------------
# SAVE
# -------------------------
def salvar_bases(bases):
    os.makedirs("bases", exist_ok=True)

    for nome, df in bases.items():
        path = f"bases/{nome}.xlsx"
        df.to_excel(path, index=False)

# -------------------------
# MAIN
# -------------------------
def main():
    bases = {
        "t_conectados_atual": gerar_conectados_atual(),
        "t_conectados_anterior": gerar_conectados_anterior(),
        "geoplan": gerar_geoplan(),
        "AuditReport": gerar_audit(),
        "sislic": gerar_sislic(),
        "infragest": gerar_infrgest()
    }

    salvar_bases(bases)


if __name__ == "__main__":
    main()
