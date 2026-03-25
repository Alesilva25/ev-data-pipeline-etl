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
    
    # Quantidades para as duas abas do AuditReport no mesmo arquivo
    QTD_AUDIT_ABA_1 = 45000 
    QTD_AUDIT_ABA_2 = 35000 

    # Criando o pool principal de IDs
    pool_ids = np.arange(10000, 90000)

    def gerar_ids(qtd):
        numeros = np.random.choice(pool_ids, size=qtd, replace=True)
        return [f"EV-{n}" for n in numeros]

    # Função auxiliar para gerar estrutura da AuditReport (tudo do mesmo mês: Março/2026)
    def gerar_df_audit(qtd):
        return pd.DataFrame({
            'CODIGO_ER 1': gerar_ids(qtd),
            'TIPO_DE_PONTO 62': np.random.choice(['SHOPPING', 'SUPERMERCADO', 'PONTO ECOLÓGICO', 'INTERNO', 'COBERTURA', 'A DEFINIR'], qtd),
            'LATITUDE 25': np.random.uniform(-33.7, -5.2, qtd),
            'LONGITUDE 27': np.random.uniform(-73.9, -34.8, qtd),
            'EMPRESA_AUDITORA': np.random.choice(['SGS', 'Bureau Veritas', 'TUV', 'Falconi', 'VisãoLocal'], qtd),
            'DATA_VISTORIA': pd.to_datetime(np.random.choice(pd.date_range('2026-03-01', '2026-03-25'), qtd)),
            'OBSERVACAO_CAMPO': np.random.choice(['Local adequado', 'Piso irregular', 'Necessita reforço', 'Sem problemas', 'Risco de alagamento'], qtd),
            'ID_VISTORIA': np.random.randint(10000, 999999, qtd),
            'NOME_INSPETOR': [f"Inspetor_{np.random.randint(1,100)}" for _ in range(qtd)],
            'FOTOS_ANEXADAS': np.random.choice(['SIM', 'NAO'], qtd),
            'RESULTADO_ESTRUTURAL': np.random.choice(['APROVADO', 'REPROVADO', 'COM RESSALVAS'], qtd),
            'NIVEL_SINAL_4G': np.random.choice(['EXCELENTE', 'BOM', 'FRACO', 'INEXISTENTE'], qtd),
            'TEMPERATURA_MEDIDA': np.round(np.random.uniform(20.0, 40.0), 1),
            'ACESSIBILIDADE_OK': np.random.choice(['SIM', 'NAO'], qtd),
            'SITUACAO_PISO': np.random.choice(['CONCRETO', 'ASFALTO', 'TERRA', 'GRAMA'], qtd)
        })

    # ==========================================
    # 1. BASES DE CONECTADOS (Atual e Anterior)
    # ==========================================
    print("Gerando Conectados Atual e Anterior...")
    
    ids_atual = [f"EV-{i}" for i in range(10000, 10000 + QTD_CONECTADOS_ATUAL)]
    df_atual = pd.DataFrame({
        'ID_ESTACAO': ids_atual,
        'STATUS CONSOLIDADO': np.random.choice(['OPERACIONAL', 'SEM CONEXÃO DE REDE', 'ESTAÇÃO EM COBERTURA', 'EM OBRAS'], len(ids_atual)),
        'STATUS_FATURAMENTO': np.random.choice([0, 1, 2], len(ids_atual)),
        'CHECKS': 'AGUARDANDO_PROCESSAMENTO',
        'MES_REFERENCIA': '03/2026',
        'EXPORTADO_POR': 'SISTEMA_BATCH',
        'DATA_PROCESSAMENTO': '2026-03-25',
        'VERSAO_PIPELINE': 'v1.5.0',
        'GESTOR_APROVADOR': np.random.choice(['Diretor A', 'Gerente B', 'Coordenador C'], len(ids_atual)),
        'TIPO_CONTRATO_LOCACAO': np.random.choice(['COMODATO', 'ALUGUEL', 'PARCERIA'], len(ids_atual)),
        'VALOR_ALUGUEL': np.round(np.random.uniform(0, 5000, len(ids_atual)), 2)
    })
    df_atual.to_excel('bases/t_conectados_atual.xlsx', index=False)

    ids_anterior = [f"EV-{i}" for i in range(10000, 10000 + QTD_CONECTADOS_ANTERIOR)]
    df_anterior = pd.DataFrame({
        'ID_ESTACAO': ids_anterior,
        'STATUS CONSOLIDADO': np.random.choice(['OPERACIONAL', 'SEM CONEXÃO DE REDE', 'ESTAÇÃO EM COBERTURA'], len(ids_anterior)),
        'STATUS_FATURAMENTO': np.random.choice([0, 1, 2], len(ids_anterior)),
        'CHECKS': 'OK',
        'MES_REFERENCIA': '02/2026',
        'EXPORTADO_POR': 'SISTEMA_BATCH',
        'DATA_PROCESSAMENTO': '2026-02-28',
        'VERSAO_PIPELINE': 'v1.4.2',
        'GESTOR_APROVADOR': np.random.choice(['Diretor A', 'Gerente B', 'Coordenador C'], len(ids_anterior)),
        'TIPO_CONTRATO_LOCACAO': np.random.choice(['COMODATO', 'ALUGUEL', 'PARCERIA'], len(ids_anterior)),
        'VALOR_ALUGUEL': np.round(np.random.uniform(0, 5000, len(ids_anterior)), 2)
    })
    df_anterior.to_excel('bases/t_conectados_anterior.xlsx', index=False)

    # ==========================================
    # 2. BASE GEOPLAN (15.000 registros | 15 Colunas)
    # ==========================================
    print("Gerando GeoPlan...")
    ids_geoplan = gerar_ids(QTD_GEOPLAN)
    df_geoplan = pd.DataFrame({
        'ID_ESTACAO': ids_geoplan,
        'TIPO_ESTACAO_GEOPLAN': np.random.choice(['SHOPPING', 'SUPERMERCADO', 'PONTO ECOLÓGICO', 'INTERNO', 'COBERTURA', 'A DEFINIR', 'NOVO_TERRENO', 'COMERCIAL'], QTD_GEOPLAN),
        'LATITUDE': np.random.uniform(-33.7, -5.2, QTD_GEOPLAN),
        'LONGITUDE': np.random.uniform(-73.9, -34.8, QTD_GEOPLAN),
        'REGIAO_COMERCIAL': np.random.choice(['SUL', 'SUDESTE', 'NORDESTE', 'CENTRO-OESTE', 'NORTE'], QTD_GEOPLAN),
        'DATA_CRIACAO_SISTEMA': pd.to_datetime(np.random.choice(pd.date_range('2022-01-01', '2026-01-01'), QTD_GEOPLAN)),
        'ANALISTA_RESPONSAVEL': np.random.choice(['João Silva', 'Maria Souza', 'Carlos Eduardo', 'Ana Paula', 'Felipe Santos', 'Mariana Costa'], QTD_GEOPLAN),
        'CENTRO_DE_CUSTO': np.random.randint(100000, 999999, QTD_GEOPLAN),
        'CIDADE': np.random.choice(['São Paulo', 'Campinas', 'Rio de Janeiro', 'Curitiba', 'Belo Horizonte', 'Salvador'], QTD_GEOPLAN),
        'ESTADO': np.random.choice(['SP', 'RJ', 'PR', 'MG', 'BA', 'SC'], QTD_GEOPLAN),
        'CEP': np.random.randint(10000000, 99999999, QTD_GEOPLAN),
        'STATUS_PROJETO': np.random.choice(['EM ESTUDO', 'APROVADO_DIRETORIA', 'ON HOLD', 'KICK-OFF'], QTD_GEOPLAN),
        'ORCAMENTO_PREVISTO': np.round(np.random.uniform(50000, 250000, QTD_GEOPLAN), 2),
        'NOME_LOCAL': [f"Local_{i}" for i in range(QTD_GEOPLAN)],
        'CONCESSIONARIA_LOCAL': np.random.choice(['Enel', 'Light', 'Copel', 'CPFL'], QTD_GEOPLAN)
    })
    df_geoplan.to_excel('bases/GeoPlan.xlsx', index=False)

    # ==========================================
    # 3. BASE AUDIT_REPORT (1 Arquivo, 2 Abas/Sheets)
    # ==========================================
    print("Gerando AuditReport (Com múltiplas abas)...")
    df_audit_1 = gerar_df_audit(QTD_AUDIT_ABA_1)
    df_audit_2 = gerar_df_audit(QTD_AUDIT_ABA_2)

    # O pd.ExcelWriter permite gravar várias abas no mesmo arquivo
    with pd.ExcelWriter('bases/AuditReport.xlsx', engine='openpyxl') as writer:
        df_audit_1.to_excel(writer, sheet_name='Lote_1', index=False)
        df_audit_2.to_excel(writer, sheet_name='Lote_2', index=False)

    # ==========================================
    # 4. BASE INFRAGEST (48.100 registros | 15 Colunas)
    # ==========================================
    print("Gerando InfraGest...")
    df_infra = pd.DataFrame({
        'PONTO_ER': gerar_ids(QTD_INFRA),
        'STATUS_INFRA': np.random.choice(['CONECTADO', 'INFRA NÃO CAPACITADA', 'PENDENTE ATIVAÇÃO', ''], QTD_INFRA),
        'FORNECEDOR_ENERGIA': np.random.choice(['Enel', 'Light', 'CPFL', 'Copel', 'Neoenergia'], QTD_INFRA),
        'TIPO_CONEXAO': np.random.choice(['TRIFÁSICA', 'MONOFÁSICA', 'BIFÁSICA'], QTD_INFRA),
        'POTENCIA_KW': np.random.choice([50, 150, 350], QTD_INFRA),
        'NUMERO_MEDIDOR': np.random.randint(1000000, 9999999, QTD_INFRA),
        'DATA_LIGACAO_PADRAO': pd.to_datetime(np.random.choice(pd.date_range('2023-01-01', '2026-01-01'), QTD_INFRA)),
        'CUSTO_MENSAL_ESTIMADO': np.round(np.random.uniform(500, 3000, QTD_INFRA), 2),
        'EMPREITEIRA_OBRA': np.random.choice(['Construtora A', 'Engenharia B', 'InfraTech'], QTD_INFRA),
        'CABO_METRAGEM': np.random.randint(10, 500, QTD_INFRA),
        'TIPO_QUADRO_ELETRICO': np.random.choice(['QGBT', 'QDC', 'QTA'], QTD_INFRA),
        'CHAVE_GTI': np.random.choice(['ATIVADA', 'DESATIVADA'], QTD_INFRA),
        'TIPO_TRAFO': np.random.choice(['PEDESTAL', 'POSTE', 'SUBTERRANEO'], QTD_INFRA),
        'ALARMES_ATIVOS': np.random.randint(0, 5, QTD_INFRA),
        'DATA_ULTIMA_MANUTENCAO': pd.to_datetime(np.random.choice(pd.date_range('2025-01-01', '2026-03-01'), QTD_INFRA))
    })
    df_infra.to_excel('bases/InfraGest.xlsx', index=False)

    # ==========================================
    # 5. BASE SISLIC (46.123 registros | 15 Colunas)
    # ==========================================
    print("Gerando SisLic...")
    df_sislic = pd.DataFrame({
        'CODIGO_ER': gerar_ids(QTD_SISLIC),
        'STATUS_SISLIC': np.random.choice(['APROVADO', 'EM ANÁLISE', 'NÃO TEM LICENÇA', 'PENDENTE INSTALAÇÃO'], QTD_SISLIC),
        'NUMERO_PROCESSO_PREFEITURA': [f"PROC-{np.random.randint(1000,9999)}" for _ in range(QTD_SISLIC)],
        'DESPACHANTE': np.random.choice(['Despachante A', 'Despachante B', 'Interno'], QTD_SISLIC),
        'DATA_ENTRADA_ORGAO': pd.to_datetime(np.random.choice(pd.date_range('2024-01-01', '2026-01-01'), QTD_SISLIC)),
        'DATA_ULTIMA_MOVIMENTACAO': pd.to_datetime(np.random.choice(pd.date_range('2025-06-01', '2026-03-01'), QTD_SISLIC)),
        'TAXA_PAGA': np.random.choice(['SIM', 'NAO'], QTD_SISLIC),
        'VALOR_TAXA': np.round(np.random.uniform(100, 1500, QTD_SISLIC), 2),
        'ORGAO_MUNICIPAL': np.random.choice(['SEPLAN', 'SMDU', 'CETESB', 'BOMBEIROS'], QTD_SISLIC),
        'TIPO_ALVARA': np.random.choice(['DEFINITIVO', 'PROVISORIO', 'ISENTO'], QTD_SISLIC),
        'RESTRICAO_AMBIENTAL': np.random.choice(['NENHUMA', 'APP', 'ZONA_TOMBADA'], QTD_SISLIC),
        'NUMERO_PROTOCOLO': np.random.randint(10000000, 99999999, QTD_SISLIC),
        'ANALISTA_PREFEITURA': np.random.choice(['Servidor_1', 'Servidor_2', 'Servidor_3'], QTD_SISLIC),
        'PRAZO_ESTIMADO_DIAS': np.random.randint(15, 180, QTD_SISLIC),
        'OBS_LICENCIAMENTO': np.random.choice(['Aguardando assinatura', 'Documentacao pendente', 'Emissao liberada', 'Em analise tecnica'], QTD_SISLIC)
    })
    df_sislic.to_excel('bases/SisLic.xlsx', index=False)

    end_time = time.time()
    print(f"✅ Sucesso! Bases geradas em {round(end_time - start_time, 2)} segundos.")