import pandas as pd
import numpy as np
import time
import os

if __name__ == '__main__':
    print("🚀 Iniciando a geração de bases em massa...")
    start_time = time.time()

    # Cria a pasta bases se não existir
    if not os.path.exists('bases'):
        os.makedirs('bases')
        print("Pasta 'bases' criada.")

    # Quantidades ajustadas
    QTD_CONECTADOS_ATUAL = 30000
    QTD_CONECTADOS_ANTERIOR = 28000 
    QTD_GEOPLAN = 15000
    QTD_INFRA = 48100
    QTD_SISLIC = 46123  
    QTD_AUDIT_ABA_1 = 45000 
    QTD_AUDIT_ABA_2 = 35000 

    # Criando o pool principal de IDs
    pool_ids = np.arange(10000, 90000)

    def gerar_ids(qtd):
        numeros = np.random.choice(pool_ids, size=qtd, replace=True)
        return [f"EV-{n}" for n in numeros]

    # Domínios de dados para facilitar a criação de divergências
    DOM_GEOPLAN = ['SHOPPING', 'SUPERMERCADO', 'PONTO ECOLÓGICO', 'INTERNO', 'COBERTURA', 'A DEFINIR', 'NOVO_TERRENO', 'COMERCIAL']
    DOM_INFRA = ['CONECTADO', 'INFRA NÃO CAPACITADA', 'PENDENTE ATIVAÇÃO', 'FORA DO AR']
    DOM_SISLIC = ['APROVADO', 'EM ANÁLISE', 'NÃO TEM LICENÇA', 'PENDENTE INSTALAÇÃO']
    DOM_AUDIT_PONTO = ['SHOPPING', 'SUPERMERCADO', 'PONTO ECOLÓGICO', 'INTERNO', 'COBERTURA', 'A DEFINIR', 'TORRE', 'POSTE']

    # ==========================================
    # 1. GERANDO AS BASES FONTES PRIMEIRO
    # ==========================================
    print("Gerando bases auxiliares (GeoPlan, InfraGest, SisLic, AuditReport)...")

    # --- GEOPLAN ---
    ids_geoplan = gerar_ids(QTD_GEOPLAN)
    df_geoplan = pd.DataFrame({
        'ID_ESTACAO': ids_geoplan,
        'TIPO_ESTACAO_GEOPLAN': np.random.choice(DOM_GEOPLAN, QTD_GEOPLAN),
        'LATITUDE': np.random.uniform(-33.7, -5.2, QTD_GEOPLAN),
        'LONGITUDE': np.random.uniform(-73.9, -34.8, QTD_GEOPLAN),
        'REGIAO_COMERCIAL': np.random.choice(['SUL', 'SUDESTE', 'NORDESTE', 'CENTRO-OESTE', 'NORTE'], QTD_GEOPLAN),
        'DATA_CRIACAO_SISTEMA': pd.to_datetime(np.random.choice(pd.date_range('2022-01-01', '2026-01-01'), QTD_GEOPLAN)),
        'ANALISTA_RESPONSAVEL': np.random.choice(['João Silva', 'Maria Souza', 'Carlos Eduardo', 'Ana Paula'], QTD_GEOPLAN)
    })
    df_geoplan.to_excel('bases/GeoPlan.xlsx', index=False)

    # --- INFRAGEST ---
    df_infra = pd.DataFrame({
        'PONTO_ER': gerar_ids(QTD_INFRA),
        'STATUS_INFRAGEST': np.random.choice(DOM_INFRA, QTD_INFRA),
        'FORNECEDOR_ENERGIA': np.random.choice(['Enel', 'Light', 'CPFL', 'Copel'], QTD_INFRA),
        'TIPO_CONEXAO': np.random.choice(['TRIFÁSICA', 'MONOFÁSICA', 'BIFÁSICA'], QTD_INFRA)
    })
    df_infra.to_excel('bases/InfraGest.xlsx', index=False)

    # --- SISLIC ---
    df_sislic = pd.DataFrame({
        'CODIGO_ER': gerar_ids(QTD_SISLIC),
        'STATUS_SISLIC': np.random.choice(DOM_SISLIC, QTD_SISLIC),
        'NUMERO_PROCESSO_PREFEITURA': [f"PROC-{np.random.randint(1000,9999)}" for _ in range(QTD_SISLIC)],
        'DESPACHANTE': np.random.choice(['Despachante A', 'Despachante B', 'Interno'], QTD_SISLIC)
    })
    df_sislic.to_excel('bases/SisLic.xlsx', index=False)

    # --- AUDIT REPORT ---
    def gerar_df_audit(qtd):
        return pd.DataFrame({
            'CODIGO_ER 1': gerar_ids(qtd),
            'TIPO_DE_PONTO 62': np.random.choice(DOM_AUDIT_PONTO, qtd),
            'LATITUDE 25': np.random.uniform(-33.7, -5.2, qtd),
            'LONGITUDE 27': np.random.uniform(-73.9, -34.8, qtd),
            'EMPRESA_AUDITORA': np.random.choice(['SGS', 'Bureau Veritas', 'TUV', 'Falconi'], qtd)
        })
    df_audit_1 = gerar_df_audit(QTD_AUDIT_ABA_1)
    df_audit_2 = gerar_df_audit(QTD_AUDIT_ABA_2)
    df_audit_full = pd.concat([df_audit_1, df_audit_2]) 

    with pd.ExcelWriter('bases/AuditReport.xlsx', engine='openpyxl') as writer:
        df_audit_1.to_excel(writer, sheet_name='Lote_1', index=False)
        df_audit_2.to_excel(writer, sheet_name='Lote_2', index=False)

    # ==========================================
    # 2. FUNÇÃO PARA GERAR DIVERGÊNCIAS NO ANTERIOR
    # ==========================================
    def gerar_coluna_divergente(ids_alvo, df_base, col_id_base, col_val_base, dominio_valores, is_coord=False):
        dict_base = df_base.set_index(col_id_base)[col_val_base].to_dict()
        valores_gerados = []
        
        for id_estacao in ids_alvo:
            if id_estacao in dict_base:
                val_real = dict_base[id_estacao]
                if np.random.rand() > 0.5:
                    valores_gerados.append(val_real) 
                else:
                    if is_coord:
                        valores_gerados.append(val_real + 0.5) 
                    else:
                        opcoes = [x for x in dominio_valores if x != val_real]
                        valores_gerados.append(np.random.choice(opcoes)) 
            else:
                valores_gerados.append(np.random.uniform(-33, -5) if is_coord else np.random.choice(dominio_valores))
                
        return valores_gerados

    # ==========================================
    # 3. BASES DE CONECTADOS (Atual e Anterior)
    # ==========================================
    print("Gerando Conectados Atual e Anterior...")
    
    ids_atual = [f"EV-{i}" for i in range(10000, 10000 + QTD_CONECTADOS_ATUAL)]
    df_atual = pd.DataFrame({
        'ID_ESTACAO': ids_atual,
        'STATUS CONSOLIDADO': np.random.choice(['OPERACIONAL', 'SEM CONEXÃO DE REDE', 'ESTAÇÃO EM COBERTURA', 'EM OBRAS'], len(ids_atual)),
        'CHECKS': 'AGUARDANDO_PROCESSAMENTO',
        'MES_REFERENCIA': '03/2026'
    })
    df_atual.to_excel('bases/t_conectados_atual.xlsx', index=False)

    ids_anterior = [f"EV-{i}" for i in range(10000, 10000 + QTD_CONECTADOS_ANTERIOR)]
    
    df_anterior = pd.DataFrame({
        # Colunas exigidas
        'ID_ESTACAO': ids_anterior,
        'STATUS CONSOLIDADO': np.random.choice(['OPERACIONAL', 'SEM CONEXÃO DE REDE', 'ESTAÇÃO EM COBERTURA'], len(ids_anterior)),
        'CHECKS': 'OK',
        'MES_REFERENCIA': '02/2026',
        'STATUS E-MAIL': np.random.choice(['ENVIADO', 'PENDENTE', 'ERRO'], len(ids_anterior)),
        'STATUS_SISLIC': gerar_coluna_divergente(ids_anterior, df_sislic, 'CODIGO_ER', 'STATUS_SISLIC', DOM_SISLIC),
        'TIPO_ESTACAO_GEOPLAN': gerar_coluna_divergente(ids_anterior, df_geoplan, 'ID_ESTACAO', 'TIPO_ESTACAO_GEOPLAN', DOM_GEOPLAN),
        'SISTEMA_ER': gerar_coluna_divergente(ids_anterior, df_infra, 'PONTO_ER', 'STATUS_INFRAGEST', DOM_INFRA),
        'TIPO_DE_PONTO 62': gerar_coluna_divergente(ids_anterior, df_audit_full, 'CODIGO_ER 1', 'TIPO_DE_PONTO 62', DOM_AUDIT_PONTO),
        'LATITUDE': gerar_coluna_divergente(ids_anterior, df_audit_full, 'CODIGO_ER 1', 'LATITUDE 25', [], is_coord=True),
        'LONGITUDE': gerar_coluna_divergente(ids_anterior, df_audit_full, 'CODIGO_ER 1', 'LONGITUDE 27', [], is_coord=True),
        
        # Novas colunas adicionadas para dar realismo (ruído)
        'GESTOR_RESPONSAVEL': np.random.choice(['Carlos Silva', 'Mariana Souza', 'Fernando Oliveira', 'Ana Costa', 'Julio Cesar', 'Beatriz Lima'], len(ids_anterior)),
        'CUSTO_MANUTENCAO_BRL': np.round(np.random.uniform(500, 25000, len(ids_anterior)), 2),
        'DATA_ULTIMA_VISTORIA': pd.to_datetime(np.random.choice(pd.date_range('2024-01-01', '2026-02-28'), len(ids_anterior))),
        'NIVEL_PRIORIDADE': np.random.choice(['ALTA', 'MÉDIA', 'BAIXA', 'CRÍTICA'], len(ids_anterior)),
        'OBSERVACOES_GERAIS': np.random.choice(['Sem pendências.', 'Aguardando liberação de acesso.', 'Equipamento oxidado.', 'Revisar no próximo ciclo.', ''], len(ids_anterior))
    })
    df_anterior.to_excel('bases/t_conectados_anterior.xlsx', index=False)

    end_time = time.time()
    print(f"✅ Sucesso! Bases geradas em {round(end_time - start_time, 2)} segundos.")