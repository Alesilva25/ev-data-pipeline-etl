Scikit learn para análise de dados
file handling
lambda
docker
tratamento try, except
Regex
Interface em Django
Criar arquivo json com lista de chaves para procv futuro
Plotly ou matplotlib
Documentação com MKdocs
Disponibilizar download das bases de testes no frontend com dados gerados pela biblioteca faker

📘 1. Visão Geral da Automação
    Esta automação realiza o processamento completo de bases relacionadas a Estações de Recarga (ERs) de veículos elétricos, consolidando informações de múltiplas fontes (Conectados Atual, Conectados Anterior, GeoPlan, AuditReport, SisLic e InfraGest), aplicando regras de negócio, detectando divergências e classificando as estações em diferentes categorias. O pipeline produz como resultado:

    Base t_conectados consolidada e classificada de Estações de Recarga (ERs)

    Arquivos Excel exportáveis

    Tabela de divergências para revisão da equipe de engenharia

    Interface Web (Django) com Dashboard interativo de métricas estratégicas

    🎯 Objetivo Geral
        Centralizar e automatizar o tratamento de dados para identificar:

        ERs operacionais e prontas para uso

        ERs com problemas de viabilidade (quebra)

        Divergências de cadastro entre os sistemas da empresa (histórico vs. atual)

        Status de faturamento/uso

        Classificação técnica e de infraestrutura

        Exportação de arquivos finais e gravação de dados no banco MySQL

        🧩 Problema que resolve

        Divergências entre bases de dados internas de diferentes setores

        Falta de padronização e inconsistências no cadastro de novos pontos

        Classificação de viabilidade feita de forma manual e suscetível a erros

        Processamento repetitivo, demorado e que consumia horas da equipe

        🖥️ Onde roda

        Interface: Django (Fullstack Web)

        Processamento: Python (Pandas/Backend)

        Armazenamento: MySQL

        Execução: Container Docker (docker-compose)

        👥 Público-alvo

        Times de Engenharia de Infraestrutura

        Arquitetura de Expansão

        Operações B2B

        Gestores de Projeto

📁 2. Arquitetura / Fluxo Geral

    Coleta (Upload dos arquivos via Interface Django)

    ⬇ Cruzamento Inicial (Conectados Atual x Conectados Anterior)

    ⬇ Padronização de colunas

    ⬇ Limpeza e normalização

    ⬇ Deduplicação (Tratamento de duplicidades no SisLic)

    ⬇ Cruzamentos (Base Inicial x GeoPlan x AuditReport x SisLic x InfraGest) (Geração programática dos sufixos _AUX para as bases fontes)

    ⬇ Tratamentos específicos por fonte de dados

    ⬇ Detecção de divergências

    ⬇ Classificação STATUS CONSOLIDADO

    ⬇ Cálculo STATUS_FATURAMENTO

    ⬇ Exportação (Excel e Banco MySQL)

    ⬇ Dashboard (KPIs e gráficos renderizados no Django)

    Dependências entre módulos

    main.py -> orquestra o pipeline de dados

    utils.py -> ferramentas genéricas (limpeza de texto, padronização)

    conexao_banco.py -> exportação MySQL (SQLAlchemy)

    views.py / templates -> roteamento web e renderização visual (Django)

    dashboard.py -> geração de gráficos (Plotly) integrados ao template HTML

    dados_dashboard.py -> funções de cálculo de métricas

🗂️ 3. Fontes de Dados e Chaves de Cruzamento

    CONECTADOS ATUAL:

    Origem: Arquivo Excel t_conectados_atual.xlsx

    Campos usados: ID_ESTACAO atua como chave mestre do mês.

    CONECTADOS ANTERIOR:

    Origem: Arquivo Excel t_conectados_anterior.xlsx

    Campos de Validação: ID_ESTACAO, STATUS CONSOLIDADO, CHECKS, MES_REFERENCIA, STATUS E-MAIL, STATUS_SISLIC, TIPO_ESTACAO_GEOPLAN, SISTEMA_ER, TIPO_DE_PONTO 62, LATITUDE, LONGITUDE.

    GEOPLAN:

    Origem: Arquivo Excel GeoPlan.xlsx

    Campos usados: ID_ESTACAO, TIPO_ESTACAO_GEOPLAN

    AUDIT_REPORT:

    Origem: Arquivo Excel AuditReport.xlsx (Múltiplas abas: Lote_1, Lote_2)

    Campos usados: CODIGO_ER 1 (Chave), TIPO_DE_PONTO 62, LATITUDE 25, LONGITUDE 27.

    SISLIC (Licenciamento):

    Origem: Arquivo Excel SisLic.xlsx

    Campos usados: CODIGO_ER (Chave), STATUS_SISLIC

    INFRAGEST:

    Origem: Arquivo Excel InfraGest.xlsx

    Campos usados: PONTO_ER (Chave), STATUS_INFRAGEST

🪄 4. Regras de Transformação e Limpeza
    1 - Regras de Cruzamento Inicial (Bases de Conectados):
        1.1 - A base conectados_atual é importada e sofre filtro onde apenas [ID_ESTACAO] atua como mestre
        1.2 - Os valores de conectados_anterior são trazidos apenas para as chaves de [ID_ESTACAO] que existirem na base atual. Chaves novas recebem valores vazios para posterior classificação

    2 - Regras da base GeoPlan:
        2.1 - Valores nulos em ['AUX_TIPO_ESTACAO_GEOPLAN'] = A DEFINIR
        2.2 - Se [TIPO_ESTACAO_GEOPLAN] == [AUX_TIPO_ESTACAO_GEOPLAN], nada é feito
        2.3 - Se [TIPO_ESTACAO_GEOPLAN] == A DEFINIR, mas não em [AUX_TIPO_ESTACAO_GEOPLAN], então [TIPO_ESTACAO_GEOPLAN] = [AUX_TIPO_ESTACAO_GEOPLAN]
        2.4 - Se [TIPO_ESTACAO_GEOPLAN] != [AUX_TIPO_ESTACAO_GEOPLAN] & [TIPO_ESTACAO_GEOPLAN] != "A DEFINIR" & [AUX_TIPO_ESTACAO_GEOPLAN] != null, então é enviado para validação

    3 - Regras da base AuditReport:
        3.1 - Se [TIPO_DE_PONTO 62] == [AUX_TIPO_DE_PONTO], nada é feito
        3.2 - Se [TIPO_DE_PONTO 62] == A DEFINIR, mas não em [AUX_TIPO_DE_PONTO 62], então [TIPO_DE_PONTO 62] == [AUX_TIPO_DE_PONTO 62]
        3.3 - ['LATITUDE', 'LONGITUDE'] = ['AUX_LATITUDE', 'AUX_LONGITUDE'] onde não está vazio

    4 - Regras da base SisLic:
        ** SisLic possui chaves repetidas em [CODIGO_ER] com status diferentes. Não devem ser excluídas de imediato
        Antes da comparação:
            caso encontre alguma chave com Status = APROVADO, então exclui outras chaves duplicadas
            se não tiver APROVADO busca EM ANÁLISE e exclui chaves duplicadas

        4.1 - Se [STATUS_SISLIC] == [AUX_STATUS_SISLIC], nada é feito
        4.2 - Se [STATUS_SISLIC] == APROVADO e [AUX_STATUS_SISLIC] != APROVADO, então devolve dados para validação manual
        4.3 - Se [STATUS_SISLIC] != APROVADO, então [STATUS_SISLIC] = [AUX_STATUS_SISLIC]

    5 - Regras da base InfraGest:
        5.1 - Se [SISTEMA_ER] == CONECTADO e [STATUS_INFRAGEST] == a CONECTADO, nada é feito
        5.2 - Se [SISTEMA_ER] == vazio, então [SISTEMA_ER] = [STATUS_INFRAGEST]
        5.3 - Se [SISTEMA_ER] == CONECTADO e [STATUS_INFRAGEST] != CONECTADO, então é enviado para validação
        5.4 - Se o valor na coluna [SISTEMA_ER] estiver vazio e o valor de [STATUS_INFRAGEST] também, então [SISTEMA_ER] é igual a INFRA NÃO CAPACITADA

    6 - Regras para classificação de ERs:
        6.1 - Se o valor na coluna [STATUS E-MAIL] estiver preenchido mantém a informação do [STATUS CONSOLIDADO] atual
        6.2 - Se o valor na coluna [AUX_TIPO_ESTACAO_GEOPLAN] for igual a SHOPPING ou SUPERMERCADO ou PONTO ECOLÓGICO, então [STATUS CONSOLIDADO] é igual a ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)
        6.3 - Se o valor na coluna [AUX_TIPO_ESTACAO_GEOPLAN] for igual a INTERNO, então [STATUS CONSOLIDADO] é igual a CARREGADOR LENTO - INTERNO
        6.4 - Se o valor na coluna [AUX_TIPO_ESTACAO_GEOPLAN] for igual a COBERTURA, então [STATUS CONSOLIDADO] é igual a ESTAÇÃO EM COBERTURA
        6.5 - Se o valor na coluna [AUX_TIPO_ESTACAO_GEOPLAN] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e [AUX_STATUS_SISLIC] for igual a APROVADO, então [STATUS CONSOLIDADO] é igual a OPERACIONAL
        6.6 - Se o valor na coluna [AUX_TIPO_ESTACAO_GEOPLAN] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e [AUX_STATUS_SISLIC] for igual a NÃO TEM LICENÇA ou PENDENTE INSTALAÇÃO, mantém os status atuais e nos campos vazios mudar para "SEM CONEXÃO DE REDE"

    7 - Regras da coluna STATUS_FATURAMENTO:
        7.1 - Se o valor na coluna [STATUS CONSOLIDADO] for igual a OPERACIONAL e [STATUS_INFRAGEST] for igual a CONECTADO ou PENDENTE ATIVAÇÃO, então [STATUS_FATURAMENTO] é igual a 1
        7.2 - Se o valor na coluna [STATUS CONSOLIDADO] for igual a OPERACIONAL e [STATUS_INFRAGEST] for igual a INFRA NÃO CAPACITADA, então [STATUS_FATURAMENTO] é igual a 0
        7.3 - Para qualquer caso que não bata com as duas condições anteriores, [STATUS_FATURAMENTO] é igual a 2

💾 5. Outputs / Resultados
Gerados automaticamente na pasta do projeto:

resultado_validacao_ers.xlsx

dados_divergentes_auditoria.xlsx (somente se divergências existirem)

t_conectados_final_corrigido.xlsx

ER_Conectada_MM-YYYY_Oficial.xlsx

Tabela no banco MySQL:

Nome: TB_VALIDACAO_ESTACAO

Banco: projetos_expansao

Modo: append

📊 6. Regras do Dashboard

Cascata ER Conectada

1.1 - ERs Totais = Valor total de chaves processadas

1.2 - Operacionais = Total de valores 'OPERACIONAL'

Python
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
====== Status Inviabilidade (Gargalos) ======
Contagem direta (value_counts) para categorias como:

SEM ALVARÁ DE INSTALAÇÃO / ALTO CUSTO - OBRAS

SEM CONEXÃO DE REDE

ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR)

DESATIVAÇÃO DE PONTO ANTIGO

ALTO INVESTIMENTO DE INFRAESTRUTURA

CABINE BLINDADA

CARREGADOR LENTO - INTERNO

OPERACIONAL - Desligue pontos antigos

ÁREA DE RISCO / PONTO DE CONCORRENTE

VIA PÚBLICA

PONTO DE APOIO

ESTAÇÃO DESATIVADA

ÁREA DE DIFÍCIL ACESSO (ZONA RURAL / ISOLADA)

====== ERs com / sem uso ======

Python
er_com_uso = t_conectados[t_conectados["STATUS_FATURAMENTO"] == 1].shape[0]
er_sem_uso = t_conectados[t_conectados["STATUS_FATURAMENTO"] == 0].shape[0]
📁 7. Estrutura do Código

Plaintext
validacao-ers/
│
├── bases/                      -> arquivos de dados brutos e scripts de geração mock
│
├── modules/
│   └── utils.py                -> ferramentas de padronização e limpeza
│
├── backend/
│   ├── main.py                 -> pipeline ETL principal (Pandas)
│   ├── conexao_banco.py        -> gravação MySQL (SQLAlchemy) e exportação
│   └── finalizar_processo.py   -> aplicação de correções manuais
│
├── core/                       -> App principal Django
│   ├── views.py                -> lógica de roteamento web e integração de dados
│   ├── urls.py                 -> mapeamento de rotas
│   └── templates/              -> arquivos HTML (interface e dashboard)
│
├── tests/                      -> suíte de testes unitários (pytest)
├── Dockerfile                  -> configuração do container da aplicação
├── docker-compose.yml          -> orquestração (Web + Banco MySQL)
├── requirements.txt            -> dependências do projeto
└── README.md                   -> documentação geral do projeto
⚙️ 8. Parâmetros Configuráveis

Caminhos internos de diretórios (backend/front)

Motores de leitura de Excel (openpyxl, xlrd)

Lista de tipos de estações sustentáveis

Lista de status operacionais

Credenciais e nome da tabela MySQL (via variáveis de ambiente / .env do Docker)

Campos considerados críticos para divergência

📄 9. Requisitos Técnicos

Python 3.10+

Django

Pandas & Numpy

Plotly (integrado no template)

SQLAlchemy & PyMySQL

openpyxl / xlrd

Docker / Docker Compose

✔️ 10. Checklist de Validação Final
Antes de aprovar e exportar os resultados da rodada:

[ ] Conferir quantidade total de ERs processadas no cruzamento Atual vs Anterior.

[ ] Verificar se as colunas essenciais nativas (SISTEMA_ER, LATITUDE, TIPO_ESTACAO_GEOPLAN, etc.) e as auxiliares dinâmicas (_AUX) existem após os merges.

[ ] Validar a deduplicação do SisLic (verificar se CODIGO_ER está único antes do merge).

[ ] Analisar a tabela de divergências geradas (falsos positivos de nomenclatura).

[ ] Conferir consistência dos indicadores renderizados no frontend (soma dos status deve bater com total geral).

[ ] Comparar os totais exportados no Excel com os inseridos na tabela TB_VALIDACAO_ESTACAO do MySQL.