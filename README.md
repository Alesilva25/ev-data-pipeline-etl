📘 1. Visão Geral da Automação
Esta automação realiza o processamento completo de bases relacionadas a Estações de Recarga (ERs) de veículos elétricos, consolidando informações de múltiplas fontes (GeoPlan, SisLic, AuditReport, InfraGest e base histórica), aplicando regras de negócio, detectando divergências e classificando as estações em diferentes categorias. O pipeline produz como resultado:

- Base consolidada e classificada de Estações de Recarga (ERs)
- Arquivos Excel exportáveis
- Tabela de divergências para revisão da equipe de engenharia
- Dashboard interativo com métricas estratégicas de expansão

🎯 Objetivo Geral
Centralizar e automatizar o tratamento de dados para identificar:

- ERs operacionais e prontas para uso
- ERs com problemas de viabilidade (quebra)
- Divergências de cadastro entre os sistemas da empresa
- Status de faturamento/uso
- Classificação técnica e de infraestrutura
- Exportação de arquivos finais e gravação de dados no banco MySQL

🧩 Problema que resolve

- Divergências entre bases de dados internas de diferentes setores
- Falta de padronização e inconsistências no cadastro de novos pontos
- Classificação de viabilidade feita de forma manual e suscetível a erros
- Processamento repetitivo, demorado e que consumia horas da equipe

🖥️ Onde roda

Interface: Streamlit
Processamento: Python (backend)
Armazenamento: MySQL
Execução: Container Docker

👥 Público-alvo

Times de Engenharia de Infraestrutura
Arquitetura de Expansão
Operações B2B
Gestores de Projeto

📁 2. Arquitetura / Fluxo Geral
Coleta (Upload dos arquivos)
  ⬇
Padronização de colunas
  ⬇
Limpeza e normalização
  ⬇
Deduplicação (SisLic)
  ⬇
Cruzamentos (GeoPlan x SisLic x AuditReport x InfraGest x Base anterior)
  ⬇
Tratamentos específicos por fonte de dados
  ⬇
Detecção de divergências
  ⬇
Classificação STATUS CONSOLIDADO
  ⬇
Cálculo STATUS FATURAMENTO
  ⬇
Exportação (Excel e Banco MySQL)
  ⬇
Dashboard (KPIs e gráficos)

Dependências entre módulos

main.py -> orquestra o pipeline
finalizar_processo.py -> corrige valores enviados manualmente
conexao_banco.py -> exporta para o MySQL
app.py -> interface web via Streamlit
dashboard.py -> geração de gráficos (Plotly)
dados_dashboard.py -> cálculo de métricas de negócio

🗂️ 3. Fontes de Dados
- GEOPLAN:
    - Origem: Arquivo Excel
    - Campos usados: ID_ESTACAO, TIPO_ESTACAO_GEOPLAN, LATITUDE, LONGITUDE

- AUDIT_REPORT:
    - Origem: Arquivo Excel
    - Campos usados: CODIGO_ER 1, TIPO_DE_PONTO 62, LATITUDE 25, LONGITUDE 27

- SISLIC (Licenciamento):
    - Origem: Arquivo Excel
    - Campos usados: CODIGO_ER, STATUS_SISLIC

- INFRAGEST:
    - Origem: Base exportada do sistema de infraestrutura
    - Campos usados: PONTO_ER, STATUS_INFRA

- BASE HISTÓRICA:
    - Origem: Arquivo interno histórico_t_procv.xlsx
    - Campos usados: STATUS CONSOLIDADO, CHECKS, FATURAMENTO etc.

🪄 4. Regras de Transformação e Limpeza
1 - Regras da base GeoPlan:
    1.1 - Todos os valores nulos em [TIPO_ESTACAO_GEOPLAN] recebem o valor A DEFINIR
    1.2 - Se [TIPO_ESTACAO_GEOPLAN] e [AUX_TIPO_PONTO_AUDIT] tiverem o mesmo valor, nada é feito
    1.3 - Se o valor na coluna [TIPO_ESTACAO_GEOPLAN] for igual a A DEFINIR, mas não em [AUX_TIPO_PONTO_AUDIT], então [TIPO_ESTACAO_GEOPLAN] assume o valor de [AUX_TIPO_PONTO_AUDIT]
    1.4 - Mantém os valores de [AUX_LATITUDE_AUDIT] e [AUX_LONGITUDE_AUDIT] e o que estiver vazio recebe [LATITUDE] e [LONGITUDE] genéricas

2 - Regras da base SisLic:
    ** SisLic tem chaves repetidas com valores de licença diferentes que não devem ser excluídas de imediato.
    Antes da comparação:
        Caso encontre alguma chave com Status = APROVADO, exclui as outras chaves duplicadas.
        Se não tiver APROVADO, busca EM ANÁLISE e exclui as chaves duplicadas restantes.

    2.1 - Se o valor na coluna [STATUS_SISLIC] e [AUX_STATUS_SISLIC] forem iguais, nada é feito
    2.2 - Se o valor na coluna [STATUS_SISLIC] for igual a APROVADO e [AUX_STATUS_SISLIC] não for APROVADO, envia para a tabela de validação
    2.3 - Se o valor na coluna [STATUS_SISLIC] for diferente de APROVADO, substitui o valor de [STATUS_SISLIC] pelo valor de [AUX_STATUS_SISLIC]

3 - Regras da base InfraGest:
    3.1 - Se o valor em [SISTEMA_ER] for igual a CONECTADO e [AUX_STATUS_INFRAGEST] for igual a CONECTADO, nada é feito
    3.2 - Se o valor em [SISTEMA_ER] estiver vazio, recebe o valor de [AUX_STATUS_INFRAGEST]
    3.3 - Se o valor em [SISTEMA_ER] for igual a CONECTADO e [AUX_STATUS_INFRAGEST] for diferente de CONECTADO, envia para validação
    3.4 - Se o valor em [SISTEMA_ER] estiver vazio e o valor de [AUX_STATUS_INFRAGEST] também, então [SISTEMA_ER] é igual a INFRA NÃO CAPACITADA

4 - Regras para classificação de ERs:
    4.1 - Se o valor na coluna [STATUS E-MAIL] estiver preenchido, mantém a informação do STATUS CONSOLIDADO
    4.2 - Se [TIPO_ESTACAO_GEOPLAN] for igual a SHOPPING ou SUPERMERCADO ou PONTO ECOLÓGICO, então [STATUS CONSOLIDADO] é igual a ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)
    4.3 - Se [TIPO_ESTACAO_GEOPLAN] for igual a INTERNO, então [STATUS CONSOLIDADO] é igual a CARREGADOR LENTO - INTERNO
    4.4 - Se [TIPO_ESTACAO_GEOPLAN] for igual a COBERTURA, então [STATUS CONSOLIDADO] é igual a ESTAÇÃO EM COBERTURA
    4.5 - Se [TIPO_ESTACAO_GEOPLAN] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e [STATUS_SISLIC] for igual a APROVADO, então [STATUS CONSOLIDADO] é igual a OPERACIONAL
    4.6 - Se [TIPO_ESTACAO_GEOPLAN] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e [STATUS_SISLIC] for igual a NÃO TEM LICENÇA ou PENDENTE INSTALAÇÃO, então [STATUS CONSOLIDADO] mantém os status atuais e nos campos vazios muda para "SEM CONEXÃO DE REDE"

5 - Regras da coluna STATUS_FATURAMENTO:
    5.1 - Se [STATUS CONSOLIDADO] for igual a OPERACIONAL e [SISTEMA_ER] for igual a CONECTADO ou PENDENTE ATIVAÇÃO, então [STATUS_FATURAMENTO] é igual a 1
    5.2 - Se [STATUS CONSOLIDADO] for igual a OPERACIONAL e [SISTEMA_ER] for igual a INFRA NÃO CAPACITADA, então [STATUS_FATURAMENTO] é igual a 0
    5.3 - Se qualquer valor não bater com uma das duas condições anteriores, então [STATUS_FATURAMENTO] é igual a 2

💾 5. Outputs / Resultados
Gerados automaticamente:

resultado_validacao_ers.xlsx
dados_divergentes_auditoria.xlsx (somente se divergências existirem)
t_conectados_final_corrigido.xlsx
ER_Conectada_MM-YYYY_Oficial.xlsx
historico_t_procv.xlsx (cópia interna de backup)

Tabela no banco MySQL:

Nome: TB_VALIDACAO_ESTACAO
Banco: projetos_expansao
Modo: append

📊 6. Regras do Dashboard
1. Cascata ER Conectada
    1.1 - ERs = Valor total de chaves processadas
    1.2 - Operacionais = Total de valores 'OPERACIONAL'

operacionais = t_conectados[
    t_conectados['STATUS CONSOLIDADO'] == 'OPERACIONAL'
].shape[0]

cobertura = t_conectados[
    t_conectados['STATUS CONSOLIDADO'] == 'ESTAÇÃO EM COBERTURA'
].shape[0]

FILTRO_QUEBRA = (
    (t_conectados["STATUS CONSOLIDADO"] != "OPERACIONAL") &
    (t_conectados["STATUS CONSOLIDADO"] != "ESTAÇÃO EM COBERTURA")
)

quebra = t_conectados.loc[FILTRO_QUEBRA, "STATUS CONSOLIDADO"].shape[0]

# ====== Status Inviabilidade (Gargalos) ======

status_counts = t_conectados["STATUS CONSOLIDADO"].value_counts()

sem_alvara = status_counts.get("SEM ALVARÁ DE INSTALAÇÃO / ALTO CUSTO - OBRAS", 0)
sem_conexao = status_counts.get("SEM CONEXÃO DE REDE", 0)
estacoes_sustentaveis = status_counts.get("ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)", 0)
desativacao_antiga = status_counts.get("DESATIVAÇÃO DE PONTO ANTIGO", 0)
alto_investimento = status_counts.get("ALTO INVESTIMENTO DE INFRAESTRUTURA", 0)
cabine_blindada = status_counts.get("CABINE BLINDADA", 0)
carregador_interno = status_counts.get("CARREGADOR LENTO - INTERNO", 0)
apto_desativacao = status_counts.get("OPERACIONAL - Desligue pontos antigos", 0)
area_risco = status_counts.get("ÁREA DE RISCO / PONTO DE CONCORRENTE", 0)
via_publica = status_counts.get("VIA PÚBLICA", 0)
ponto_apoio = status_counts.get("PONTO DE APOIO", 0)
estacao_desativada = status_counts.get("ESTAÇÃO DESATIVADA", 0)
dificil_acesso = status_counts.get("ÁREA DE DIFÍCIL ACESSO (ZONA RURAL / ISOLADA)", 0)

total_geral = (
    sem_alvara + sem_conexao + estacoes_sustentaveis + desativacao_antiga +
    alto_investimento + cabine_blindada + carregador_interno + apto_desativacao +
    area_risco + via_publica + ponto_apoio + estacao_desativada + dificil_acesso
)

# ====== ERs com / sem uso ======

er_com_uso = t_conectados[t_conectados["STATUS_FATURAMENTO"] == 1].shape[0]
er_sem_uso = t_conectados[t_conectados["STATUS_FATURAMENTO"] == 0].shape[0]

📁 7. Estrutura do Código
validacao-ers/
│
├── backend/
│   ├── main.py                 -> pipeline principal (Pandas)
│   ├── conexao_banco.py        -> gravação MySQL (SQLAlchemy) e exportação
│   └── finalizar_processo.py   -> aplicação de correções manuais
│
├── frontend/
│   ├── app.py                  -> interface web Streamlit
│   ├── dashboard.py            -> gráficos dinâmicos (Plotly)
│   ├── dados_dashboard.py      -> funções de cálculo de métricas
│   └── images/                 -> assets visuais do sistema
│
├── tests/                      -> suíte de testes unitários (pytest)
├── README.md                   -> documentação geral do projeto
└── .streamlit/                 -> configurações de tema da interface

⚙️ 8. Parâmetros Configuráveis

Caminhos internos de diretórios (backend/front)
Motores de leitura de Excel (openpyxl, xlrd)
Lista de tipos de estações sustentáveis
Lista de status operacionais
Credenciais e nome da tabela MySQL (via .env)
Campos considerados críticos para divergência
Layout customizado do dashboard

📄 9. Requisitos Técnicos
Linguagens / Infraestrutura

Python 3.10+
Streamlit
Pandas
Numpy
Plotly
SQLAlchemy
PyMySQL
openpyxl / xlrd
Docker

✔️ 10. Checklist de Validação Final
Antes de aprovar e exportar os resultados da rodada:

1. Conferir quantidade total de ERs processadas
2. Verificar se colunas essenciais existem após os merges
3. Validar tipagem de dados (numéricos / strings)
4. Analisar a tabela de divergências geradas
5. Conferir consistência dos indicadores no dashboard
6. Comparar os totais com o processamento do mês anterior