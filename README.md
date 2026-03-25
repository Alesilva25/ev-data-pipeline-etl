📘 1. Visão Geral da Automação
Esta automação realiza o processamento completo de bases relacionadas a Estações de Recarga (ERs) de veículos elétricos, consolidando informações de múltiplas fontes (Conectados Atual, Conectados Anterior, GeoPlan, SisLic, AuditReport e InfraGest), aplicando regras de negócio, detectando divergências e classificando as estações em diferentes categorias. O pipeline produz como resultado:

- Base consolidada e classificada de Estações de Recarga (ERs)
- Arquivos Excel exportáveis
- Tabela de divergências para revisão da equipe de engenharia
- Interface Web (Django) com Dashboard interativo de métricas estratégicas

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
  ⬇
Concatenação de bases particionadas (AuditReport Lotes 1 e 2)
  ⬇
Cruzamento Inicial (Conectados Atual x Conectados Anterior)
  ⬇
Limpeza e normalização
  ⬇
Deduplicação (SisLic)
  ⬇
Cruzamentos (Base Inicial x GeoPlan x SisLic x AuditReport x InfraGest)
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
Dashboard (KPIs e gráficos renderizados no Django)

Dependências entre módulos

main.py -> orquestra o pipeline de dados
utils.py -> ferramentas genéricas (limpeza de texto, padronização)
conexao_banco.py -> exportação MySQL (SQLAlchemy)
views.py / templates -> roteamento web e renderização visual (Django)
dashboard.py -> geração de gráficos (Plotly) integrados ao template HTML
dados_dashboard.py -> funções de cálculo de métricas

🗂️ 3. Fontes de Dados
- CONECTADOS ATUAL:
    - Origem: Arquivo Excel t_conectados_atual.xlsx (Exportado com diversas colunas brutas)
    - Campos usados: Apenas ID_ESTACAO é filtrado via código para atuar como chave mestre do mês.

- CONECTADOS ANTERIOR:
    - Origem: Arquivo Excel t_conectados_anterior.xlsx
    - Campos usados: ID_ESTACAO, STATUS CONSOLIDADO, CHECKS, STATUS_FATURAMENTO etc.

- GEOPLAN:
    - Origem: Arquivo Excel
    - Campos usados: ID_ESTACAO, TIPO_ESTACAO_GEOPLAN, LATITUDE, LONGITUDE

- AUDIT_REPORT:
    - Origem: Arquivo Excel único dividido em múltiplas abas (ex: Lote_1 e Lote_2)
    - Campos usados: CODIGO_ER 1, TIPO_DE_PONTO 62, LATITUDE 25, LONGITUDE 27

- SISLIC (Licenciamento):
    - Origem: Arquivo Excel
    - Campos usados: CODIGO_ER, STATUS_SISLIC

- INFRAGEST:
    - Origem: Base exportada do sistema de infraestrutura
    - Campos usados: PONTO_ER, STATUS_INFRA

🪄 4. Regras de Transformação e Limpeza
    1 - Regras de Cruzamento Inicial (Bases de Conectados):
        1.1 - A base conectados_atual é importada e passa por um filtro de seleção onde apenas a coluna conectados_atual['ID_ESTACAO'] é mantida para servir como mestre.
        1.2 - Os valores das colunas da base conectados_anterior são trazidos (Left Join) apenas para as chaves de conectados_atual['ID_ESTACAO'] que existirem na base atual. Chaves novas recebem valores vazios para posterior classificação.

    2 - Regras da base GeoPlan:
        2.1 - Todos os valores nulos em geoplan['TIPO_ESTACAO_GEOPLAN'] recebem o valor A DEFINIR.
        2.2 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] e audit_report['AUX_TIPO_PONTO_AUDIT'] tiverem o mesmo valor, nada é feito.
        2.3 - Se o valor na coluna geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a A DEFINIR, mas não em audit_report['AUX_TIPO_PONTO_AUDIT'], então geoplan['TIPO_ESTACAO_GEOPLAN'] assume o valor de audit_report['AUX_TIPO_PONTO_AUDIT'].
        2.4 - Mantém os valores de audit_report['AUX_LATITUDE_AUDIT'] e audit_report['AUX_LONGITUDE_AUDIT'] e o que estiver vazio recebe as coordenadas de geoplan['LATITUDE'] e geoplan['LONGITUDE'] genéricas.

    3 - Regras da base SisLic:
        ** sislic tem chaves repetidas em sislic['CODIGO_ER'] com valores de licença diferentes que não devem ser excluídas de imediato.
        Antes da comparação:
            Caso encontre alguma chave com sislic['STATUS_SISLIC'] = APROVADO, exclui as outras chaves duplicadas.
            Se não tiver APROVADO, busca EM ANÁLISE e exclui as chaves duplicadas restantes.

        3.1 - Se o valor na coluna base_consolidada['STATUS_SISLIC'] e sislic['AUX_STATUS_SISLIC'] forem iguais, nada é feito.
        3.2 - Se o valor na coluna base_consolidada['STATUS_SISLIC'] for igual a APROVADO e sislic['AUX_STATUS_SISLIC'] não for APROVADO, envia para a tabela de validação.
        3.3 - Se o valor na coluna base_consolidada['STATUS_SISLIC'] for diferente de APROVADO, substitui o valor de base_consolidada['STATUS_SISLIC'] pelo valor de sislic['AUX_STATUS_SISLIC'].

    4 - Regras da base InfraGest:
        4.1 - Se o valor em base_consolidada['SISTEMA_ER'] for igual a CONECTADO e infragest['AUX_STATUS_INFRAGEST'] for igual a CONECTADO, nada é feito.
        4.2 - Se o valor em base_consolidada['SISTEMA_ER'] estiver vazio, recebe o valor de infragest['AUX_STATUS_INFRAGEST'].
        4.3 - Se o valor em base_consolidada['SISTEMA_ER'] for igual a CONECTADO e infragest['AUX_STATUS_INFRAGEST'] for diferente de CONECTADO, envia para validação.
        4.4 - Se o valor em base_consolidada['SISTEMA_ER'] estiver vazio e o valor de infragest['AUX_STATUS_INFRAGEST'] também, então base_consolidada['SISTEMA_ER'] é igual a INFRA NÃO CAPACITADA.

    5 - Regras para classificação de ERs:
        5.1 - Se o valor na coluna base_consolidada['STATUS E-MAIL'] estiver preenchido, mantém a informação de base_consolidada['STATUS CONSOLIDADO'].
        5.2 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a SHOPPING ou SUPERMERCADO ou PONTO ECOLÓGICO, então base_consolidada['STATUS CONSOLIDADO'] é igual a ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR).
        5.3 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a INTERNO, então base_consolidada['STATUS CONSOLIDADO'] é igual a CARREGADOR LENTO - INTERNO.
        5.4 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a COBERTURA, então base_consolidada['STATUS CONSOLIDADO'] é igual a ESTAÇÃO EM COBERTURA.
        5.5 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e sislic['STATUS_SISLIC'] for igual a APROVADO, então base_consolidada['STATUS CONSOLIDADO'] é igual a OPERACIONAL.
        5.6 - Se geoplan['TIPO_ESTACAO_GEOPLAN'] for igual a A DEFINIR ou NOVO_TERRENO ou COMERCIAL e sislic['STATUS_SISLIC'] for igual a NÃO TEM LICENÇA ou PENDENTE INSTALAÇÃO, então base_consolidada['STATUS CONSOLIDADO'] mantém os status atuais e nos campos vazios muda para "SEM CONEXÃO DE REDE".

    6 - Regras da coluna STATUS_FATURAMENTO:
        6.1 - Se base_consolidada['STATUS CONSOLIDADO'] for igual a OPERACIONAL e infragest['SISTEMA_ER'] for igual a CONECTADO ou PENDENTE ATIVAÇÃO, então base_consolidada['STATUS_FATURAMENTO'] é igual a 1.
        6.2 - Se base_consolidada['STATUS CONSOLIDADO'] for igual a OPERACIONAL e infragest['SISTEMA_ER'] for igual a INFRA NÃO CAPACITADA, então base_consolidada['STATUS_FATURAMENTO'] é igual a 0.
        6.3 - Se qualquer valor não bater com uma das duas condições anteriores, então base_consolidada['STATUS_FATURAMENTO'] é igual a 2.

💾 5. Outputs / Resultados
Gerados automaticamente:

resultado_validacao_ers.xlsx
dados_divergentes_auditoria.xlsx (somente se divergências existirem)
t_conectados_final_corrigido.xlsx
ER_Conectada_MM-YYYY_Oficial.xlsx

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
├── bases/                      -> arquivos de dados brutos e gerador mock
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
Credenciais e nome da tabela MySQL (via variáveis de ambiente / Docker)
Campos considerados críticos para divergência

📄 9. Requisitos Técnicos
Linguagens / Infraestrutura

Python 3.10+
Django
Pandas
Numpy
Plotly (integrado no template)
SQLAlchemy
PyMySQL
openpyxl / xlrd
Docker / Docker Compose

✔️ 10. Checklist de Validação Final
Antes de aprovar e exportar os resultados da rodada:

1. Conferir quantidade total de ERs processadas
2. Verificar se colunas essenciais existem após os merges
3. Validar tipagem de dados (numéricos / strings)
4. Analisar a tabela de divergências geradas
5. Conferir consistência dos indicadores renderizados no frontend
6. Comparar os totais com o processamento do mês anterior