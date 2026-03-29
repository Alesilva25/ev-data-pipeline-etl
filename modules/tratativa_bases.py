import pandas as pd

def carregar_bases():
    '''
    - Carrega GeoPlan, InfraGest e SisLic com colunas específicas.
    - Consolida todas as abas do AuditReport em um único DataFrame.
    - Realiza o Left Join da base Atual com a Anterior.

    Params:
        Nenhum (Lê arquivos do diretório 'bases/').

    Return:
        tuple: (df_geoPlan, df_infraGest, df_sisLic, df_connected, df_auditReport)
    '''
    # Lista com caminhos dos arquivos de bases
    df_geoPlan = pd.read_excel(r"bases\GeoPlan.xlsx", usecols=['ID_ESTACAO', 'TIPO_ESTACAO_GEOPLAN'])
    df_infraGest = pd.read_excel(r"bases\InfraGest.xlsx", usecols=['PONTO_ER', 'STATUS_INFRAGEST'])
    df_sisLic = pd.read_excel(r"bases\SisLic.xlsx", usecols=['CODIGO_ER', 'STATUS_SISLIC'])
    df_connectedPrevious = pd.read_excel(r"bases\t_conectados_anterior.xlsx")
    df_connectedCurrent = pd.read_excel(r"bases\t_conectados_atual.xlsx", usecols=['ID_ESTACAO'])

    # Aba 1 do arquivo AuditReport
    df_auditReport = pd.concat(
        pd.read_excel(r"bases\AuditReport.xlsx", sheet_name=None, usecols=['CODIGO_ER 1', 'TIPO_DE_PONTO 62', 'LATITUDE 25', 'LONGITUDE 27']).values(),
        ignore_index=True
    )
    
    # Faz merge do connectedCurrent com conectadosAntigo
    df_connected = df_connectedCurrent.merge(df_connectedPrevious, on='ID_ESTACAO', how='left')

    return df_geoPlan, df_infraGest, df_sisLic, df_connected, df_auditReport

def juntar_bases(df_geoPlan, df_infraGest, df_sisLic, df_connected, df_auditReport):
    '''
    - Realiza o merge entre a base mestre e as bases auxiliares e remove colunas de ID duplicadas (PONTO_ER, CODIGO_ER 1)
    - Aplica o prefixo 'AUX_' para diferenciar colunas auxiliares das originais.

    Params:
        df_geoPlan (pd.DataFrame): Dados de tipologia oficial do GeoPlan.
        df_infraGest (pd.DataFrame): Status de infraestrutura e conexão.
        df_sisLic (pd.DataFrame): Base de licenciamento (retornada para tratamento posterior).
        df_connected (pd.DataFrame): Base mestre de conectados (Atual + Anterior).
        df_auditReport (pd.DataFrame): Dados consolidados de auditoria física.

    Return:
        tuple: (df_connected enriquecido, df_sisLic)
    '''
    # juntar bases conectados
    df_connected = (
        df_connected
        .merge(df_geoPlan, on= 'ID_ESTACAO', how= 'left', suffixes=("", '_2'))
        .merge(df_infraGest, left_on= 'ID_ESTACAO', right_on= 'PONTO_ER', how= 'left', suffixes=("", '_2'))
        .merge(df_auditReport, left_on= 'ID_ESTACAO', right_on= 'CODIGO_ER 1', how= 'left', suffixes=("", '_2'))
        .drop(columns=['PONTO_ER', 'CODIGO_ER 1'], errors='ignore')
        )

    # Adiciona prefixo AUX_ nas colunas auxiliares
    df_connected = df_connected.rename(columns={
        'TIPO_ESTACAO_GEOPLAN_2': 'AUX_TIPO_ESTACAO_GEOPLAN', 
        'STATUS_INFRAGEST_2': 'AUX_STATUS_INFRAGEST',
        'TIPO_DE_PONTO 62_2': 'AUX_TIPO_DE_PONTO',
        'LATITUDE 25': 'AUX_LATITUDE',
        'LONGITUDE 27': 'AUX_LONGITUDE'
        })

    return df_connected, df_sisLic

def tratar_geoPlan(df_connected):
    '''
    '''
    # Preenche valores nulos em ['AUX_TIPO_ESTACAO_GEOPLAN'] por A DEFINIR.
    df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] = df_connected['AUX_TIPO_ESTACAO_GEOPLAN'].fillna('A DEFINIR')
    
    # Se [TIPO_ESTACAO_GEOPLAN] == A DEFINIR, mas não em [AUX_TIPO_ESTACAO_GEOPLAN], então [TIPO_ESTACAO_GEOPLAN] = [AUX_TIPO_ESTACAO_GEOPLAN]
    FILTRO = (df_connected['TIPO_ESTACAO_GEOPLAN'] == "A DEFINIR") & (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] != "A DEFINIR")
    df_connected.loc[FILTRO, 'TIPO_ESTACAO_GEOPLAN'] = df_connected['AUX_TIPO_ESTACAO_GEOPLAN']

    return df_connected

def tratar_sisLic(df_connected, df_sisLic):
        # Prioriza os valores
        prioridade = {
                'APROVADO': 1,
                'EM ANALISE': 2,
        }

        # Prioriza os valores em uma nova coluna
        df_sisLic['PRIORIDADE'] = df_sisLic['STATUS_SISLIC'].map(prioridade).fillna(99)

        # Ordena por prioridade e exclui outras duplicadas
        df_sisLic = (
                df_sisLic
                .sort_values(by=['CODIGO_ER', 'PRIORIDADE'])
                .drop_duplicates(subset='CODIGO_ER', keep='first')
                .rename(columns={'STATUS_SISLIC': 'AUX_STATUS_SISLIC'})
                .drop(columns=['PRIORIDADE'], errors='ignore')
        )

        # Faz merge da df_connected com df_sisLic
        df_connected = df_connected.merge(df_sisLic, left_on='ID_ESTACAO', right_on='CODIGO_ER', how='left')
 
        # Se [STATUS_SISLIC] == [AUX_STATUS_SISLIC], então não faz nada
        # Se [STATUS_SISLIC] == APROVADO e [AUX_STATUS_SISLIC] != APROVADO, então cria a tabela divergencia_sisLic 
        filtro_divergencia = ((df_connected['STATUS_SISLIC'] == 'APROVADO') & (df_connected['AUX_STATUS_SISLIC'] != 'APROVADO'))
        divergencia_sisLic = df_connected.loc[filtro_divergencia, ['ID_ESTACAO', 'STATUS_SISLIC', 'AUX_STATUS_SISLIC']].copy()

        # Se [STATUS_SISLIC] != APROVADO, então [STATUS_SISLIC] = [AUX_STATUS_SISLIC]
        df_connected['STATUS_SISLIC'] = df_connected['STATUS_SISLIC'].mask(df_connected['STATUS_SISLIC'] != 'APROVADO', df_connected['AUX_STATUS_SISLIC'])

        return df_connected, divergencia_sisLic