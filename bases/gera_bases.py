import pandas as pd
import numpy as np
import time
import os

if __name__ == '__main__':
    print("🧪 Gerando bases com DIVERGÊNCIAS e LIMBOS (A DEFINIR duplo)...")
    start_time = time.time()

    if not os.path.exists('bases'):
        os.makedirs('bases')

    QTD = 10000
    pool_ids = [f"EV-{i}" for i in range(10000, 10000 + QTD)]
    DOM_TIPOS = ['SHOPPING', 'SUPERMERCADO', 'PONTO ECOLÓGICO', 'INTERNO', 'COBERTURA', 'NOVO_TERRENO', 'COMERCIAL']

    # --- 1. T_CONECTADOS_ANTERIOR ---
    # Metade da base nasce como 'A DEFINIR'
    tipos_anterior = (['A DEFINIR'] * (QTD // 2)) + list(np.random.choice(DOM_TIPOS, QTD // 2))
    
    df_anterior = pd.DataFrame({
        'ID_ESTACAO': pool_ids,
        'TIPO_ESTACAO_GEOPLAN': tipos_anterior,
        'LATITUDE': 0.0,
        'LONGITUDE': 0.0,
        'STATUS_SISLIC': 'PENDENTE',
        'SISTEMA_ER': 'DESCONHECIDO',
        'MES_REFERENCIA': '02/2026'
    })

    # --- 2. GEOPLAN (COM CENÁRIOS DE PERSISTÊNCIA DE 'A DEFINIR') ---
    tipos_geoplan = []
    for i in range(QTD):
        if tipos_anterior[i] == 'A DEFINIR':
            # 60% de chance de o GeoPlan ter o dado (Regra 2.3)
            # 40% de chance de CONTINUAR 'A DEFINIR' (Para testar o limbo)
            if np.random.rand() > 0.4:
                tipos_geoplan.append(np.random.choice(DOM_TIPOS))
            else:
                tipos_geoplan.append('A DEFINIR')
        else:
            # Para quem já tem tipo, criamos divergência (Regra 2.2)
            possiveis = [t for t in DOM_TIPOS if t != tipos_anterior[i]]
            tipos_geoplan.append(np.random.choice(possiveis))

    df_geoplan = pd.DataFrame({
        'ID_ESTACAO': pool_ids,
        'TIPO_ESTACAO_GEOPLAN': tipos_geoplan
    })

    # --- 3. AUDIT REPORT (DANDO UMA ÚLTIMA CHANCE NO BLOCO 3) ---
    # Aqui também vamos deixar alguns 'A DEFINIR' para ver se a regra 3.2 mantém o estado
    tipos_audit = []
    for i in range(QTD):
        # 70% de chance de a auditoria ter o dado, 30% de vir vazio
        tipos_audit.append(np.random.choice(DOM_TIPOS) if np.random.rand() > 0.3 else 'A DEFINIR')

    df_audit = pd.DataFrame({
        'CODIGO_ER 1': pool_ids,
        'TIPO_DE_PONTO 62': tipos_audit,
        'LATITUDE 25': np.random.uniform(-23.5, -23.6, QTD),
        'LONGITUDE 27': np.random.uniform(-46.6, -46.7, QTD)
    })

    # --- SALVANDO TUDO ---
    df_anterior.to_excel('bases/t_conectados_anterior.xlsx', index=False)
    df_geoplan.to_excel('bases/GeoPlan.xlsx', index=False)
    pd.DataFrame({'ID_ESTACAO': pool_ids}).to_excel('bases/t_conectados_atual.xlsx', index=False)
    pd.DataFrame({'PONTO_ER': pool_ids, 'STATUS_INFRAGEST': 'CONECTADO'}).to_excel('bases/InfraGest.xlsx', index=False)
    pd.DataFrame({'CODIGO_ER': pool_ids, 'STATUS_SISLIC': 'APROVADO'}).to_excel('bases/SisLic.xlsx', index=False)
    
    with pd.ExcelWriter('bases/AuditReport.xlsx') as writer:
        df_audit.to_excel(writer, sheet_name='Lote_1', index=False)

    print(f"✅ Bases geradas com sucesso!")
    print(f"💡 Esperado: O contador de 'A DEFINIR' NÃO deve chegar a zero após a Regra 2.3.")