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
    try:
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

    except FileNotFoundError as error:
        print(f"Arquivo não encontrado: {error.filename}")
    
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
    # Valores nulos em ['AUX_TIPO_ESTACAO_GEOPLAN'] = A DEFINIR.
    df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] = df_connected['AUX_TIPO_ESTACAO_GEOPLAN'].fillna('A DEFINIR')
    
    # Se [TIPO_ESTACAO_GEOPLAN] == A DEFINIR, mas não em [AUX_TIPO_ESTACAO_GEOPLAN], então [TIPO_ESTACAO_GEOPLAN] = [AUX_TIPO_ESTACAO_GEOPLAN]
    FILTRO_PREENCHIMENTO = (
        (df_connected['TIPO_ESTACAO_GEOPLAN'] == "A DEFINIR") & 
        (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] != "A DEFINIR"))
    df_connected.loc[FILTRO_PREENCHIMENTO, 'TIPO_ESTACAO_GEOPLAN'] = df_connected['AUX_TIPO_ESTACAO_GEOPLAN']

    # Se [TIPO_ESTACAO_GEOPLAN] != [AUX_TIPO_ESTACAO_GEOPLAN] & [TIPO_ESTACAO_GEOPLAN] != "A DEFINIR" & [AUX_TIPO_ESTACAO_GEOPLAN] != null, então é enviado para validação
    COND_DIVERGENCIA = (
        (df_connected['TIPO_ESTACAO_GEOPLAN'] != "A DEFINIR") & 
        (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] != "A DEFINIR") & 
        (df_connected['TIPO_ESTACAO_GEOPLAN'] != df_connected['AUX_TIPO_ESTACAO_GEOPLAN'])
        )
    divergencia_geoPlan = df_connected.loc[COND_DIVERGENCIA, ['ID_ESTACAO', 'TIPO_ESTACAO_GEOPLAN', 'AUX_TIPO_ESTACAO_GEOPLAN']].copy()

    return df_connected, divergencia_geoPlan

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
        )

        # Faz merge da df_connected com df_sisLic
        df_connected = df_connected.merge(df_sisLic, left_on='ID_ESTACAO', right_on='CODIGO_ER', how='left')
 
        # Se [STATUS_SISLIC] == [AUX_STATUS_SISLIC], nada é feito
        # Se [STATUS_SISLIC] == APROVADO e [AUX_STATUS_SISLIC] != APROVADO, então devolve dados para validação manual
        COND_DIVERGENCIA = ((df_connected['STATUS_SISLIC'] == 'APROVADO') & (df_connected['AUX_STATUS_SISLIC'] != 'APROVADO'))
        divergencia_sisLic = df_connected.loc[COND_DIVERGENCIA, ['ID_ESTACAO', 'STATUS_SISLIC', 'AUX_STATUS_SISLIC']].copy()

        # Se [STATUS_SISLIC] != APROVADO, então [STATUS_SISLIC] = [AUX_STATUS_SISLIC]
        df_connected['STATUS_SISLIC'] = df_connected['STATUS_SISLIC'].mask(df_connected['STATUS_SISLIC'] != 'APROVADO', df_connected['AUX_STATUS_SISLIC'])

        return df_connected, divergencia_sisLic

def tratar_auditReport(df_connected):
        # Se [TIPO_DE_PONTO 62] == [AUX_TIPO_DE_PONTO], nada é feito
        
        # Se [TIPO_DE_PONTO 62] == A DEFINIR, mas não em [AUX_TIPO_DE_PONTO], então [TIPO_DE_PONTO 62] == [AUX_TIPO_DE_PONTO]
        COND = ((df_connected['TIPO_DE_PONTO 62'] == 'A DEFINIR') & (df_connected['AUX_TIPO_DE_PONTO'] != "A DEFINIR"))
        df_connected.loc[COND, 'TIPO_DE_PONTO 62'] = df_connected['AUX_TIPO_DE_PONTO']

        # ['LATITUDE', 'LONGITUDE'] = ['AUX_LATITUDE', 'AUX_LONGITUDE'] onde não está vazio
        df_connected['LATITUDE'] = df_connected['AUX_LATITUDE'].combine_first(df_connected['LATITUDE'])
        df_connected['LONGITUDE'] = df_connected['AUX_LONGITUDE'].combine_first(df_connected['LONGITUDE'])

        COND_DIVERGENCIA = (
                (df_connected['TIPO_DE_PONTO 62'] != "A DEFINIR") &
                (df_connected['AUX_TIPO_DE_PONTO'] != "A DEFINIR") &
                (df_connected['TIPO_DE_PONTO 62'] != df_connected['AUX_TIPO_DE_PONTO'])
                )
        divergencia_audit = df_connected.loc[COND_DIVERGENCIA, ['ID_ESTACAO', 'TIPO_DE_PONTO 62', 'AUX_TIPO_DE_PONTO']].copy()

        return df_connected, divergencia_audit

def tratar_infraGest(df_connected):
        # Se [SISTEMA_ER] == CONECTADO e [STATUS_INFRAGEST] == a CONECTADO, nada é feito
        # Se [SISTEMA_ER] == vazio, então [SISTEMA_ER] = [STATUS_INFRAGEST]
        COND_ER_NULL = ((df_connected['SISTEMA_ER'].isna()) & (df_connected['STATUS_INFRAGEST'].notna()))
        df_connected.loc[COND_ER_NULL, 'SISTEMA_ER'] = df_connected['STATUS_INFRAGEST']

        # 5.4 - Se [SISTEMA_ER] == vazio e [STATUS_INFRAGEST] também, então [SISTEMA_ER] = INFRA NÃO CAPACITADA
        COND_ALL_NULL = (
                (df_connected['SISTEMA_ER'].isna()) & 
                (df_connected['STATUS_INFRAGEST'].isna())
                )
        df_connected.loc[COND_ALL_NULL, 'SISTEMA_ER'] = 'INFRA NÃO CAPACITADA'
        
        # Se [SISTEMA_ER] == CONECTADO e [STATUS_INFRAGEST] != CONECTADO, então é enviado para validação
        COND_DIVERGENCIA = (
                (df_connected['SISTEMA_ER'] == 'CONECTADO') & 
                (df_connected['STATUS_INFRAGEST'] != 'CONECTADO')
                )
        divergencia_infraGest = df_connected.loc[COND_DIVERGENCIA, ['ID_ESTACAO', 'SISTEMA_ER', 'STATUS_INFRAGEST']].copy()

        return df_connected, divergencia_infraGest

def classificar_ERs(df_connected):
    # Se o valor na coluna [STATUS E-MAIL] estiver preenchido mantém a informação do [STATUS CONSOLIDADO] atual
    EMAIL_VAZIO = df_connected['STATUS_EMAIL'].isna()
    # Se [AUX_TIPO_ESTACAO_GEOPLAN] == SHOPPING ou SUPERMERCADO, então [STATUS CONSOLIDADO] = ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)  
    COND_SUSTENTAVEIS = ((EMAIL_VAZIO) & (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'].isin(['SHOPPING', 'SUPERMERCADO'])))
    df_connected.loc[COND_SUSTENTAVEIS, 'STATUS_CONSOLIDADO'] = 'ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)'

    # Se [AUX_TIPO_ESTACAO_GEOPLAN] == 'INTERNO', então [STATUS CONSOLIDADO] = 'CARREGADOR LENTO - INTERNO'
    COND_INTERNO = ((EMAIL_VAZIO) & (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] == 'INTERNO'))
    df_connected.loc[COND_INTERNO, 'STATUS_CONSOLIDADO'] = 'CARREGADOR LENTO - INTERNO'

    # Se [AUX_TIPO_ESTACAO_GEOPLAN] == 'COBERTURA', então [STATUS CONSOLIDADO] = 'ESTAÇÃO EM COBERTURA'
    COND_COBERTURA = ((EMAIL_VAZIO) & (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'] == 'COBERTURA'))
    df_connected.loc[COND_COBERTURA, 'STATUS_CONSOLIDADO'] = 'ESTAÇÃO EM COBERTURA'

    # Se [AUX_TIPO_ESTACAO_GEOPLAN] == 'A DEFINIR' ou 'NOVO_TERRENO' ou 'COMERCIAL' e [AUX_STATUS_SISLIC] == APROVADO, então [STATUS CONSOLIDADO] = OPERACIONAL
    COND_OPERACIONAL = (
        (EMAIL_VAZIO) & 
        (df_connected['AUX_TIPO_ESTACAO_GEOPLAN'].isin(['A DEFINIR', 'NOVO_TERRENO', 'COMERCIAL'])) &
        (df_connected['AUX_STATUS_SISLIC'] == 'APROVADO')
        )
    df_connected.loc[COND_OPERACIONAL, 'STATUS_CONSOLIDADO'] = 'OPERACIONAL'
    
    return df_connected

def definir_faturamento(df_connected):
        # Se [STATUS CONSOLIDADO] == 'OPERACIONAL' e [STATUS_INFRAGEST] == 'CONECTADO', então [STATUS_FATURAMENTO] = 1
        COND_FATURAMENTO_1 = (
            (df_connected['STATUS_CONSOLIDADO'] == 'OPERACIONAL') &
            (df_connected['STATUS_INFRAGEST'] == 'CONECTADO')
            )
        df_connected.loc[COND_FATURAMENTO_1, 'STATUS_FATURAMENTO'] = 1

        # Se [STATUS CONSOLIDADO] == OPERACIONAL e [STATUS_INFRAGEST] == INFRA NÃO CAPACITADA, então [STATUS_FATURAMENTO] = 0
        COND_FATURAMENTO_0 = (
            (df_connected['STATUS_CONSOLIDADO'] == 'OPERACIONAL') &
            (df_connected['STATUS_INFRAGEST'] == 'NÃO CONECTADO')
        )
        df_connected.loc[COND_FATURAMENTO_0, 'STATUS_FATURAMENTO'] = 0

        # Para qualquer caso que não bata com as duas condições anteriores, [STATUS_FATURAMENTO] é igual a 2
        COND_DIFERENTE = (
            (COND_FATURAMENTO_1 == False) & 
            (COND_FATURAMENTO_0 == False)
            )
        df_connected.loc[COND_DIFERENTE, 'STATUS_FATURAMENTO'] = 2

        # Exclui colunas auxiliares
        df_connected = df_connected.drop(columns=['CODIGO_ER', 'PRIORIDADE', 'AUX_STATUS_SISLIC', 'AUX_TIPO_ESTACAO_GEOPLAN', 'STATUS_INFRAGEST', 'AUX_LATITUDE', 'AUX_LONGITUDE', 'AUX_TIPO_DE_PONTO'], errors='ignore')
    
        return df_connected

def retornar_divergencia(divergencia_sisLic, divergencia_infraGest, divergencia_geoPlan, divergencia_audit):
    dados_divergentes = (
        divergencia_sisLic
        .merge(divergencia_infraGest, on='ID_ESTACAO', how='left')
        .merge(divergencia_geoPlan, on='ID_ESTACAO', how='left')
        .merge(divergencia_audit, on='ID_ESTACAO', how='left')
        )
    
    return dados_divergentes

def main():
    print("Carregando bases...")
    df_geoPlan, df_infraGest, df_sisLic, df_connected, df_auditReport = carregar_bases()

    print("Juntando bases...")
    df_connected, df_sisLic = juntar_bases(df_geoPlan, df_infraGest, df_sisLic, df_connected, df_auditReport)

    print("Tratando base geoPlan...")
    df_connected, divergencia_geoPlan = tratar_geoPlan(df_connected)

    print("Tratando base sisLic...")
    df_connected, divergencia_sisLic = tratar_sisLic(df_connected, df_sisLic)

    print("Tratando base auditReport...")
    df_connected, divergencia_audit = tratar_auditReport(df_connected)

    print("Tratando base infraGest...")
    df_connected, divergencia_infraGest = tratar_infraGest(df_connected)

    print("Gerando base com dados divergentes para validação manual...")
    dados_divergentes = retornar_divergencia(divergencia_sisLic, divergencia_infraGest, divergencia_geoPlan, divergencia_audit)

    print("Classificando ER's...")
    df_connected = classificar_ERs(df_connected)

    print("Definindo faturamento...")
    df_connected = definir_faturamento(df_connected)

    print("Organizando as colunas...")
    nova_ordem = ['ID_ESTACAO', 'STATUS_CONSOLIDADO', 'STATUS_FATURAMENTO', 'STATUS_EMAIL', 'TIPO_ESTACAO_GEOPLAN', 'STATUS_SISLIC', 'CHECKS', 'SISTEMA_ER', 'TIPO_DE_PONTO 62', 'MES_REFERENCIA', 'LATITUDE', 'LONGITUDE']
    df_connected = df_connected[nova_ordem]

    return df_connected, dados_divergentes