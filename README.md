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
        1.1 - A base conectados_atual é importada e sofre filtro onde apenas conectados_atual['ID_ESTACAO'] atua como mestre.

        1.2 - Os valores de conectados_anterior são trazidos (Left Join) apenas para as chaves de ID_ESTACAO que existirem na base atual. Chaves novas recebem valores vazios para posterior classificação.

    2 - Regras da base GeoPlan e AuditReport:
        2.1 - Todos os valores nulos em geoplan['TIPO_ESTACAO_GEOPLAN_AUX'] recebem o valor A DEFINIR.

        2.2 - Se t_conectados['TIPO_ESTACAO_GEOPLAN'] for igual a geoplan['TIPO_ESTACAO_GEOPLAN_AUX'], nada é feito. Se houver divergência de nomeclatura/tipo com a base oficial GeoPlan ou com audit['TIPO_DE_PONTO 62_AUX'], a regra de prioridade de tipologia deve ser aplicada.

        2.3 - Se o valor em t_conectados['TIPO_ESTACAO_GEOPLAN'] for igual a A DEFINIR, ele deve assumir o valor auditado em audit['TIPO_DE_PONTO 62_AUX'].

        2.4 - A automação deve cruzar as coordenadas (LATITUDE vs audit['LATITUDE 25_AUX'] e LONGITUDE vs audit['LONGITUDE 27_AUX']). Campos vazios ou divergentes na base principal recebem as coordenadas provindas da auditoria.

    3 - Regras da base SisLic:
        Atenção: sislic possui chaves repetidas em CODIGO_ER com status diferentes que não devem ser excluídas de imediato.

        Caso encontre alguma chave com STATUS_SISLIC = APROVADO antes da comparação, exclui as outras duplicadas.

        Se não tiver APROVADO, busca EM ANÁLISE e exclui as duplicadas restantes.

        3.1 - Se t_conectados['STATUS_SISLIC'] e sislic['STATUS_SISLIC_AUX'] forem iguais, nada é feito.

        3.2 - Se t_conectados['STATUS_SISLIC'] for APROVADO e sislic['STATUS_SISLIC_AUX'] NÃO for APROVADO (ex: revogado), envia o registro para a tabela de validação de divergências.

        3.3 - Se t_conectados['STATUS_SISLIC'] for diferente de APROVADO, atualiza-se substituindo o valor antigo de t_conectados pelo valor de sislic['STATUS_SISLIC_AUX'].

    4 - Regras da base InfraGest:
        4.1 - Se t_conectados['SISTEMA_ER'] for igual a CONECTADO e infragest['STATUS_INFRAGEST_AUX'] for igual a CONECTADO, nada é feito.

        4.2 - Se t_conectados['SISTEMA_ER'] estiver vazio, recebe o valor de infragest['STATUS_INFRAGEST_AUX'].

        4.3 - Se t_conectados['SISTEMA_ER'] for igual a CONECTADO e infragest['STATUS_INFRAGEST_AUX'] for diferente de CONECTADO, envia para validação de queda/desconexão.

        4.4 - Se ambos (t_conectados['SISTEMA_ER'] e infragest['STATUS_INFRAGEST_AUX']) estiverem vazios, então t_conectados['SISTEMA_ER'] recebe INFRA NÃO CAPACITADA.

    5 - Regras para classificação de ERs:
        5.1 - Se t_conectados['STATUS E-MAIL'] estiver preenchido, mantém a informação de t_conectados['STATUS CONSOLIDADO'] atual.

        5.2 - Se geoplan['TIPO_ESTACAO_GEOPLAN_AUX'] for igual a SHOPPING ou SUPERMERCADO ou PONTO ECOLÓGICO, então t_conectados['STATUS CONSOLIDADO'] é igual a ESTAÇÕES SUSTENTÁVEIS (ENERGIA SOLAR).

        5.3 - Se o tipo for INTERNO, então STATUS CONSOLIDADO = CARREGADOR LENTO - INTERNO.

        5.4 - Se o tipo for COBERTURA, então STATUS CONSOLIDADO = ESTAÇÃO EM COBERTURA.

        5.5 - Se o tipo for A DEFINIR, NOVO_TERRENO ou COMERCIAL E o licenciamento (sislic['STATUS_SISLIC_AUX']) for igual a APROVADO, então STATUS CONSOLIDADO = OPERACIONAL.

        5.6 - Se o tipo for um dos acima E a licença for NÃO TEM LICENÇA ou PENDENTE INSTALAÇÃO, mantém os status atuais. Em campos vazios muda para SEM CONEXÃO DE REDE.

    6 - Regras da coluna STATUS_FATURAMENTO:
        6.1 - Se t_conectados['STATUS CONSOLIDADO'] for OPERACIONAL e o sistema de infraestrutura atual (infragest['STATUS_INFRAGEST_AUX']) for CONECTADO ou PENDENTE ATIVAÇÃO, então STATUS_FATURAMENTO = 1.

        6.2 - Se STATUS CONSOLIDADO for OPERACIONAL e a infra for INFRA NÃO CAPACITADA, então STATUS_FATURAMENTO = 0.

        6.3 - Para qualquer caso que não bata com as duas condições anteriores, STATUS_FATURAMENTO = 2.

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