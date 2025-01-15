import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px

################## DATASET #############################

def main():
    df_espec = pd.read_csv('dataset.csv',encoding="UTF-8")
    dados= df_espec.copy()
    df_espec.drop(['CD_CNES','TIPO',],axis=1, inplace=True)
    novo_nome = {'DS_ESPECIALIDADE':'Especialidade','DS_DADO':'Tipo Atendimento','ANO':'Ano',
        'Grupos-K': 'Grupos', 'NM_REGIAO_SAUDE': 'Região de Saúde', 
        'Outlier_Combinado':'Anomalias (CB)','outliers_iso':'Anomalias','PORTE_HOSP':'Tipo do Hospital',}
    df_espec = df_espec.rename(columns=novo_nome)

    df =df_espec.copy()


########### FILTROS TAB  ###########
    def criar_filtros(lista_filtro,key1,key2):
        """Cria dois selectboxes com opções diferentes e retorna as seleções."""

        # Inicializa o estado da sessão (com valores padrão para evitar erros iniciais)
        if 'sel_1' not in st.session_state:
            st.session_state.sel_1 = lista_filtro[1]
        if 'sel_2' not in st.session_state:
            st.session_state.sel_2 = lista_filtro[0]

        # Primeiro selectbox
        sel_1 = st.selectbox('Selecione o primeiro filtro', lista_filtro, key=key1, index=lista_filtro.index(st.session_state.sel_1))
        st.session_state.sel_1 = sel_1

        # Filtra as opções para o segundo selectbox
        lista_filtro_2 = [opcao for opcao in lista_filtro if opcao != sel_1]

        # Garante que sel_2 seja válido após a mudança de sel_1
        if st.session_state.sel_2 == sel_1:
            st.session_state.sel_2 = lista_filtro_2[0] if lista_filtro_2 else None

        # Segundo selectbox (só aparece se houver opções disponíveis)
        if lista_filtro_2:
            sel_2 = st.selectbox('Selecione o segundo filtro', lista_filtro_2, key=key2, index=lista_filtro_2.index(st.session_state.sel_2) if st.session_state.sel_2 in lista_filtro_2 else 0)
            st.session_state.sel_2 = sel_2
        else:
            st.warning("Não há opções disponíveis para o segundo filtro após a seleção do primeiro.")
            sel_2 = None #retorna None quando não tem opções

        return sel_1, sel_2

 ##################################################


    def grafico_rea_meta(df):
        espec_unicos = df.Especialidade.unique().tolist()
        espec_com_todos = ["Todas"] + espec_unicos
        espec_selecionada = st.selectbox('Selecione a Especialidade:', espec_unicos, key="select_espec3")

        if espec_selecionada == "Todas":
            df_filtrado = df
        else:
            df_filtrado = df[df['Especialidade'] == espec_selecionada]
        
        df_agrupado2 = df_filtrado.groupby(['Ano', 'Especialidade','Tipo Atendimento']).agg({'QTD_PROD': 'sum', 'QTD_META': 'sum'}).reset_index()
        df_agrupado = df_agrupado2.melt(id_vars=['Ano', 'Especialidade','Tipo Atendimento'], value_vars=['QTD_PROD', 'QTD_META'], var_name='Tipo', value_name='Quantidade')
        #fig = px.bar(df_agrupado, x="Especialidade", y="Quantidade", color="Tipo", barmode="group")
        fig = px.bar(df_agrupado, x="Tipo Atendimento", y="Quantidade", color="Tipo", barmode="group")
        st.plotly_chart(fig,use_container_width=True)

        



##################### TAB 04 - DESEMPENHO POR ESPECIALIDADE ############################

    def grafico_ranking_espec(df):

        espec_unicos = df.Especialidade.unique().tolist()
        espec_com_todos = ["Todas"] + espec_unicos
            #anos_unicos.insert(0, 'Todos')
        espec_selecionada = st.selectbox('Selecione a Especialidade:', espec_unicos,key="select_espec")

            # Filtrando os dados
        if espec_selecionada== "Todas":
            df_filtrado = df
        else:
            df_filtrado = df[df['Especialidade']== espec_selecionada]
        
        grafico_espec01 = alt.Chart(df_filtrado).mark_bar(point=True).encode(
            x=alt.X('Ano:O', title='Ano'),
            y=alt.Y("sum(QTD_PROD):Q", title='Atendimentos'),
            color=alt.Color('Ano:O', title='Ano',scale=alt.Scale(
                            range=['#2171b5','#6baed6','#bdd7e7']))
        ).transform_window(
            rank="rank()",
            sort=[alt.SortField("QTD_PROD", order="descending")],
            groupby=["Ano"]
        ).properties(
            
            width=800, height=600,
        )

        # Adiciona a camada de meta e texto acima da barra
        line = alt.Chart(df_filtrado).mark_line(color="#c30010").encode(
            x=alt.X('Ano:O', title='Ano'),
            y=alt.Y("sum(QTD_META):Q", title='Meta'),
        )

        point = line.mark_point(color="#c30010")
        
        text = grafico_espec01.mark_text(dy=-8).encode( # dy ajusta a posição vertical do texto (-5 move o texto para cima)
            text='sum(QTD_PROD):Q',  # 'Q' indica que 'Valor' é um campo quantitativo
            color = alt.value('black')
        )

        grafico_ranking_espec01 = grafico_espec01 + text  # Combina as duas camadas
        return  grafico_ranking_espec01


################### TAB 03 ##########################
######## COMPARATIVO ATENDIMENTO X META  ##################

    def gera_grafico_meta_atend(df):
        if not df.empty:
            anos_unicos = df.Ano.unique().tolist()
            anos_com_todos = ["Todos"] + anos_unicos
            #anos_unicos.insert(0, 'Todos')
            ano_selecionado = st.selectbox('Selecione o ano:', anos_com_todos,key="select_ano")

            # Filtrando os dados
            if ano_selecionado == "Todos":
                df_filtrado = df
            else:
                df_filtrado = df[df['Ano']== int(ano_selecionado)]

           
            df_filtrado0=df_filtrado.rename(columns={'QTD_PROD': 'Atendimento', 'QTD_META': 'Meta'})  
            df_agrupado2 = df_filtrado0.groupby(['Ano', 'Especialidade']).agg({'Atendimento': 'sum', 'Meta': 'sum'}).reset_index()
            df_agrupado = df_agrupado2.melt(id_vars=['Ano', 'Especialidade'], value_vars=['Atendimento', 'Meta'], var_name='Tipo', value_name='Quantidade')
            fig = px.bar(df_agrupado, x="Especialidade", y="Quantidade", color="Tipo", barmode="group")
            st.plotly_chart(fig,use_container_width=True)



 ################ TAB02:  Tipo de Atendimento por Região ##############################

 
    def grafico_regiao(df):
        espec_unicos = df['Região de Saúde'].unique().tolist()
        espec_unicos.sort()
        espec_com_todos = ["Todas"] + espec_unicos
        espec_selecionada = st.selectbox('Selecione a Região de Saúde:', espec_com_todos, key="select_espec00")

        if espec_selecionada == "Todas":
            df_filtrado = df
        else:
            df_filtrado = df[df['Região de Saúde'] == espec_selecionada]
        
        df_agrupado2 = df_filtrado.groupby(['Ano', 'Região de Saúde','Tipo Atendimento']).agg({'QTD_PROD': 'sum', 'QTD_META': 'sum'}).reset_index()
        df_agrupado = df_agrupado2.melt(id_vars=['Ano', 'Região de Saúde','Tipo Atendimento'], value_vars=['QTD_PROD', 'QTD_META'], var_name='Tipo', value_name='Quantidade')
        #fig = px.bar(df_agrupado, x="Especialidade", y="Quantidade", color="Tipo", barmode="group")
        fig = px.bar(df_agrupado, x="Tipo Atendimento", y="Quantidade", color="Tipo", barmode="group")
        st.plotly_chart(fig,use_container_width=True)



############# TAB 01 - HeatMap ############

    def grafico_heatmap_altair(df,filtro_1,filtro_2):
        # Aplica os filtros ao seu DataFrame original
        if filtro_1 and filtro_2:
            try:

                df_filtrado = df.groupby([filtro_1, filtro_2])['QTD_PROD'].sum().unstack()
    
                df_filtrado = df_filtrado.fillna(0)
    
                if not df_filtrado.empty:
         
                    df_filtrado.index = df_filtrado.index.astype(str)
                    df_filtrado.columns = df_filtrado.columns.astype(str)

                    df_melted = df_filtrado.reset_index().melt(id_vars=filtro_1, var_name=filtro_2, value_name='QTD_PROD')
        
                    # Criar o heatmap com Altair (agora com dados filtrados)
                    heatmap = alt.Chart(df_melted).mark_rect().encode(
                            x=alt.X(f'{filtro_2}:N', sort='y',axis=alt.Axis(labelAngle=-45, labelFontSize=12, labelFontWeight="bold")),
                            y=alt.Y(f'{filtro_1}:N', sort='x',axis=alt.Axis(labelFontSize=12,labelFontWeight="bold")),
                            
                            color=alt.Color('QTD_PROD:Q', title='Número de Atendimentos',scale=alt.Scale(
                            range=['#ffffcc','#c7e9b4','#7fcdbb','#41b6c4','#1d91c0','#225ea8','#0c2c84']
                
                )),
                            tooltip=[f'{filtro_1}:N',f'{filtro_2}:N','QTD_PROD:Q', alt.Tooltip('QTD_PROD:Q', format='..0f')]
                        ).properties(
                            width=600,
                            height=600
                        ).interactive()

                    # Adiciona os valores numéricos dentro dos retângulos
                    text = heatmap.mark_text().encode(
                        text=alt.Text('QTD_PROD:Q', format = '.0f')
                        
                    )

                    final_chart = heatmap + text
                    st.altair_chart(final_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Ocorreu um erro durante a geração do gráfico: {e}")

################### TABS ###########################

    ########## TAB 01 ###########
    with aba1:
        #st.subheader('Análise de Padrões')
        titulo = f'<H2> Análise de Padrões'
        st.markdown(titulo, unsafe_allow_html=True)
        lista_filtro = ['Especialidade', 'Região de Saúde', 'Tipo do Hospital', 'Tipo Atendimento','Grupos', 'Anomalias']
        key1='heat_alt01'
        key2='heat_alt02'
        filtro_1, filtro_2 = criar_filtros(lista_filtro,key1,key2)
        grafico_heatmap_altair(df,filtro_1, filtro_2)
      
      ########## TAB 02 ###########  
    with aba2:
        titulo = f'<H2> Tipo de Atendimento por Região de Saúde'
        st.markdown(titulo, unsafe_allow_html=True)
        grafico_regiao(df) 
      
     ########## TAB 03 ###########
    with aba3:
        titulo = f'<H2> Atendimento x Meta por Ano'
        st.markdown(titulo, unsafe_allow_html=True)
        grafico_aba3 = gera_grafico_meta_atend(df)
        if grafico_aba3:
            st.altair_chart(grafico_aba3,use_container_width=True)
     ########## TAB 04 ###########
    with aba4:
        titulo = f'<H2> Desempenho por Tipo de Atendimento'
        st.markdown(titulo, unsafe_allow_html=True)
        grafico_rea_meta(df)
    ########## TAB 05 ###########
    with aba5: 
        titulo = f'<H2> Comparativo Anual de Atendimentos'
        st.markdown(titulo, unsafe_allow_html=True)
        st.altair_chart(grafico_ranking_espec(df))
        #st.altair_chart(grafico_ranking_espec02(df))

#################### INICIO #########################

if __name__ == "__main__":
    #pd.set_option( 'display.float_format' , lambda x: '%.3f' % x)
    center_css = """
    <style>

    div[class*="stAppDeployButton"],div[class*="StatusWidget"],span#MainMenu {
    visibility: hidden;
    }

    </style>
    """
    #st.set_page_config(layout="wide")
    st.title("Monitoramento Assistir - SES")
   

    aba1, aba2, aba3, aba4,aba5 = st.tabs(
                [

                    
                    "Análise de Padrões", 
                    "Análise por Região",
                    "Análise por Especialidade",
                    "Tipo de Atendimento",
                    "Desempenho Anual"
    
                ])
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.markdown(center_css, unsafe_allow_html=True)
    
    main()
