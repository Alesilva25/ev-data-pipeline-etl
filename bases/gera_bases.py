import pandas as pd
import numpy as np
import os

# ==============================
# CONFIG
# ==============================
BASE_PATH = 'bases'
QTD = 85000

# ==============================
# DOMÍNIOS (EXPANDIDOS)
# ==============================
def expandir_dominios(lista):
    extras = [f"{item}_ALT" for item in lista]
    return lista + extras

DOM_TIPOS = expandir_dominios([
    'SHOPPING', 'SUPERMERCADO', 'PONTO ECOLOGICO', 'INTERNO',
    'COBERTURA', 'A DEFINIR', 'NOVO_TERRENO', 'COMERCIAL'
])

DOM_SISLIC = expandir_dominios([
    'APROVADO', 'EM ANALISE', 'NAO TEM LICENCA', 'PENDENTE INSTALACAO'
])

DOM_INFRA = expandir_dominios([
    'CONECTADO', 'PENDENTE ATIVACAO', 'INFRA NAO CAPACITADA', 'ERRO_LEITURA'
])

REGIONAIS = ['SP1', 'SP2', 'RJ1', 'MG1', 'SUL1']

VENDORS = [
    'ERICSSON', 'HUAWEI', 'NOKIA', 'SIEMENS',
    'ZTE', 'CISCO', 'INTELBRAS'
]

RESPONSAVEIS = [
    'EQUIPE_SP', 'EQUIPE_RJ', 'EQUIPE_MG',
    'PMO_NACIONAL', 'TIME_FIELD'
]

# ==============================
# UTILS
# ==============================
def garantir_pasta():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)


def gerar_ids(qtd):
    return [f"EV-{i}" for i in range(10000, 10000 + qtd)]


def gerar_lat_long(qtd):
    lat = np.random.uniform(-23.9, -23.1, qtd)
    long = np.random.uniform(-46.9, -46.1, qtd)

    mask = np.random.choice([True, False], qtd, p=[0.8, 0.2])

    lat = np.where(mask, lat, 0.0)
    long = np.where(mask, long, 0.0)

    return lat, long


# ==============================
# 1. BASE MESTRE
# ==============================
def criar_base_mestre(pool_ids):
    df = pd.DataFrame({
        'ID_ESTACAO': pool_ids,
        'DATA_CARGA': '28/03/2026',
        'SISTEMA_ORIGEM': 'SAP_PRODUCAO',
        'PROJETO_NOME': np.random.choice([
            'EXPANSAO_LOTE_A', 'REMANEJAMENTO_2026', 'BACKLOG_VIVO'
        ], QTD),
        'REGIONAL_SITE': np.random.choice(REGIONAIS, QTD),
        'COD_PATRIMONIO': [f"PAT-{np.random.randint(100000, 999999)}" for _ in range(QTD)],
        'RESPONSAVEL_PMO': np.random.choice(RESPONSAVEIS, QTD),
        'NIVEL_PRIORIDADE': np.random.choice([1, 2, 3], QTD, p=[0.5, 0.3, 0.2]),
        'ESTADO_ATIVO': np.random.choice(['ATIVO', 'INATIVO', 'MANUTENCAO'], QTD, p=[0.7, 0.1, 0.2]),
        'DATA_ENTRADA_SISTEMA': '01/01/2026'
    })

    df.to_excel(f'{BASE_PATH}/t_conectados_atual.xlsx', index=False)


# ==============================
# 2. BASE ANTERIOR
# ==============================
def criar_base_anterior(pool_ids):
    lat, long = gerar_lat_long(80000)

    df = pd.DataFrame({
        'ID_ESTACAO': pool_ids[:80000],
        'TIPO_ESTACAO_GEOPLAN': np.random.choice(DOM_TIPOS, 80000),
        'LATITUDE': lat,
        'LONGITUDE': long,
        'STATUS_SISLIC': np.random.choice(DOM_SISLIC, 80000),
        'SISTEMA_ER': np.random.choice(['CONECTADO', 'DESCONECTADO', 'DESCONHECIDO'], 80000),
        'STATUS_EMAIL': np.random.choice(['FINALIZADO', 'PENDENTE'], 80000, p=[0.3, 0.7]),
        'STATUS_CONSOLIDADO': 'A_CLASSIFICAR',
        'COORD_X_SIG': np.random.uniform(1000, 2000, 80000),
        'VERSAO_BASE': 'V_2025_FINAL',
        'EQUIPAMENTO_HW': np.random.choice(VENDORS, 80000),
        'ULTIMO_LOGIN_TECNICO': 'ADMIN_SISTEMA',
        'FLAG_HISTORICO': 1,
        'OBSERVACOES_MIGRACAO': 'MIGRADO',
        'REDE_TRANSMISSAO': np.random.choice(['MW_RADIO', 'FIBRA', 'SATELITE'], 80000),
        'CAPACIDADE_MW': np.random.choice(['1Gbps', '2Gbps', '10Gbps'], 80000)
    })

    df.to_excel(f'{BASE_PATH}/t_conectados_anterior.xlsx', index=False)


# ==============================
# 3. GEOPLAN
# ==============================
def criar_geoplan(pool_ids):
    df = pd.DataFrame({
        'ID_ESTACAO': pool_ids[:70000],
        'TIPO_ESTACAO_GEOPLAN': np.random.choice(DOM_TIPOS, 70000),
        'AUX_COORDENADOR': np.random.choice(['MARCOS', 'ANA', 'JOAO', 'CARLA'], 70000),
        'ENDERECO_LOGRADOURO': 'RUA SIMULADA',
        'BAIRRO_SIG': np.random.choice(['CENTRO', 'ZONA_SUL', 'ZONA_NORTE'], 70000),
        'ZONA_COORDENACAO': np.random.choice(['NORTE', 'SUL', 'LESTE', 'OESTE'], 70000),
        'COD_GEO_REFERENCIA': [f"GEO-{i}" for i in range(70000)],
        'METRAGEM_ESTIMADA': np.random.choice([30, 50, 70, 100], 70000),
        'TIPO_CONTRATO': np.random.choice(['LOCACAO', 'PROPRIO'], 70000),
        'DATA_PLAN_GEO': '15/02/2026'
    })

    df.to_excel(f'{BASE_PATH}/GeoPlan.xlsx', index=False)


# ==============================
# 4. AUDITORIA
# ==============================
def criar_audit(pool_ids):
    lat, long = gerar_lat_long(75000)

    df = pd.DataFrame({
        'CODIGO_ER 1': pool_ids[:75000],
        'TIPO_DE_PONTO 62': np.random.choice(DOM_TIPOS, 75000),
        'LATITUDE 25': lat,
        'LONGITUDE 27': long,
        'ALTURA_ANTENA': np.random.choice([20, 30, 40], 75000),
        'OBSTR_VISUAL': np.random.choice(['SIM', 'NAO'], 75000),
        'TECNICO_CAMPO': np.random.choice(['JOAO', 'CARLOS', 'PEDRO'], 75000),
        'STATUS_LAUDO': np.random.choice(['APROVADO', 'REPROVADO'], 75000),
        'DATA_INSPECAO': '20/03/2026',
        'TIPO_SUPORTE': np.random.choice(['GREENFIELD', 'ROOFTOP'], 75000),
        'POTENCIA_LIDA_DBM': np.random.randint(-80, -50, 75000)
    })

    with pd.ExcelWriter(f'{BASE_PATH}/AuditReport.xlsx') as writer:
        df.to_excel(writer, sheet_name='INSPECAO', index=False)


# ==============================
# 5. SISLIC (CORRIGIDO)
# ==============================
def criar_sislic(pool_ids):
    ids_final = []
    status_final = []

    ids_base = pool_ids[:60000]

    for id_ in ids_base:
        # obrigatório
        ids_final.append(id_)
        status_final.append('EM ANALISE')

        # chance de aprovado
        if np.random.rand() < 0.4:
            ids_final.append(id_)
            status_final.append('APROVADO')

        # outros status
        outros = [
            s for s in DOM_SISLIC
            if 'EM ANALISE' not in s and 'APROVADO' not in s
        ]

        qtd_extras = np.random.randint(0, 3)

        for _ in range(qtd_extras):
            ids_final.append(id_)
            status_final.append(np.random.choice(outros))

    total = len(ids_final)

    df = pd.DataFrame({
        'CODIGO_ER': ids_final,
        'STATUS_SISLIC': status_final,
        'VENCIMENTO_ALVARA': '2028-12-31',
        'NUM_PROCESSO': [f"PROC-{np.random.randint(1000,9999)}" for _ in range(total)],
        'ORGAO_REGULADOR': np.random.choice(['ANATEL', 'PREFEITURA'], total),
        'ANALISTA_RESP': np.random.choice(['ANA', 'BRUNO', 'CARLA'], total),
        'PRIORIDADE_LEGAL': np.random.choice(['ALTA', 'MEDIA', 'BAIXA'], total)
    })

    df.to_excel(f'{BASE_PATH}/SisLic.xlsx', index=False)


# ==============================
# 6. INFRA
# ==============================
def criar_infra(pool_ids):
    df = pd.DataFrame({
        'PONTO_ER': pool_ids[:82000],
        'STATUS_INFRAGEST': np.random.choice(DOM_INFRA, 82000),
        'TIPO_CONEXAO': np.random.choice(['FIBRA', 'RADIO', 'SATELITE'], 82000),
        'MODEM_SERIAL': [f"SN-{np.random.randint(10000,99999)}" for _ in range(82000)],
        'CAPACIDADE_PORTA': np.random.choice(['1G', '10G'], 82000),
        'FABRICANTE_ONT': np.random.choice(VENDORS, 82000),
        'ESTADO_FONTE_ENERGIA': np.random.choice(['NORMAL', 'FALHA'], 82000)
    })

    df.to_excel(f'{BASE_PATH}/InfraGest.xlsx', index=False)


# ==============================
# MAIN
# ==============================
def main():
    garantir_pasta()
    pool_ids = gerar_ids(QTD)

    criar_base_mestre(pool_ids)
    criar_base_anterior(pool_ids)
    criar_geoplan(pool_ids)
    criar_audit(pool_ids)
    criar_sislic(pool_ids)
    criar_infra(pool_ids)

    print("✅ Mockup realista gerado com sucesso!")


if __name__ == '__main__':
    main()