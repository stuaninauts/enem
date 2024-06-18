import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
import faicons as fa
import plotly.express as px
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly
from shinywidgets import output_widget, render_widget  

ICONS = {
    "book": fa.icon_svg("book"),
    "calculator": fa.icon_svg("calculator"),
    "chart-bar": fa.icon_svg("chart-bar"),
    "arrow-up": fa.icon_svg("arrow-up"),
    "ellipsis": fa.icon_svg("ellipsis"),
    "info": fa.icon_svg("info"),
}

# am for acertos e melhoras
df_am = pd.read_csv("enem_acertos_melhoras.csv")
# cc for conversao de conhecimento
df_cc = pd.read_csv("enem_conversao_conhecimento.csv")

dict_areas = {
    # name          # beuaty name
    'linguagens':   'Linguagens',
    'humanas':      'Ciências Humanas',    
    'matematica':   'Matemática',          
    'natureza':     'Ciências da Natureza'
}

dict_questoes = {
    's': 'Questões que eu sabia',
    's_e':  'Questões que sabia e errei',
    'ns': 'Questões que eu não sabia',
    'ns_e': 'Questões que eu não sabia e errei',
}

# TODO: make single discipline analysis
dict_hum_expandida = {
    'hist': 'História',
    'geo': 'Geografia',
    'filo':   'Filosofia',
    'socio': 'Sociologia',
}

dict_nat_expandida = {
    'quim': 'Química',
    'fis': 'Física',
    'bio': 'Biologia',
}


# given color and factor, darken this color with this factor
# def darken_color(cor, factor):
#     color_rgb = mcolors.to_rgb(cor)
#     new_color_rgb = tuple(comp * (1 - factor) for comp in color_rgb)
#     new_color = mcolors.to_hex(new_color_rgb)
#     return new_color

# show the checkbox_areas_am if 'Escolher área(s)' is pressed in radio_areas
# in acertos e melhora tab
def show_checkbox_areas():
    return [
        ui.card(
            ui.card_header("Escolher análise:"),
            ui.input_checkbox_group(
                id="checkbox_areas_am",
                label="",
                choices={chave: valor for chave, valor in dict_areas.items()},
                selected=list(dict_areas.keys()),
            ),
            ui.hr(style="margin: 0;"),
            ui.input_checkbox(
                id="checkbox_acertos", 
                label=ui.tooltip(
                        ui.span("Comparar acertos com a primeira tentativa"),
                        "Para alguns simulados realizei duas tentativas, então podemos comparar os acertos de cada uma",
                        placement="right",
                        id="tooltip_comparar_acertos",
                ),
                value=False,
            ),

        ),

    ]

# nav that show acertos e melhoras related to df_am
def nav_acertos_melhoras():
    return [
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_radio_buttons(
                    id="radio_ordem_am", 
                    label="Ordem das edições:",
                    choices={'0': "Alfabética", '1': ui.tooltip(
                            ui.span("Cronológica por Resolução"),
                            "Para alguns simulados (não todos) tenho a ordem que eles foram realizados",
                            placement="right",
                            id="tooltip_ordem_edicoes_am",)},
                    selected='0',
                ),
                ui.input_radio_buttons(
                    id="radio_area", 
                    label="Área:", 
                    choices={'0': "Redação", '1': "Escolher área(s)"},
                    selected='1',
                ),
                ui.navset_hidden(
                    ui.nav_panel(None, "", value='0'),
                    ui.nav_panel(None, show_checkbox_areas(), value='1'),
                    id="nav_radio_area",
                ),    
            ),
            ui.layout_columns(
                ui.value_box(
                    "Simulados Realizados", ui.output_ui("simulados_realizados"), showcase=ICONS["book"]
                ),
                ui.value_box(
                    "Média de Acertos / Total", ui.output_ui("media_acertos_total"), showcase=ICONS["calculator"]
                ),
                ui.value_box(
                    "Média de acertos por área",
                    ui.output_ui("media_acertos_area"),
                    showcase=ICONS["chart-bar"],
                    class_='text-left',
                ),
            fill=False,
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Dados"), ui.output_data_frame("am_table"), full_screen=True
                ),
                ui.card(
                    ui.card_header(
                        "Quantidade de acertos vs edição",
                        class_="d-flex justify-content-between align-items-center",
                    ),
                    output_widget("plot_am"),
                    full_screen=True,
                ),
                ui.output_ui("secao_comparar_acertos"), # only shows up when comparar acertos is active
                col_widths=[4, 8, 12],
            ),
        )
    ]

# nav that show conversao de conhecimento related to df_cc
def nav_conversao_conhecimento():
    return [
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_radio_buttons(
                    id="radio_ordem_cc", 
                    label="Ordem das edições:",
                    choices={'0': "Alfabética", '1': ui.tooltip(
                            ui.span("Cronológica por Resolução"),
                            "Para alguns simulados (não todos) tenho a ordem que eles foram realizados",
                            placement="right",
                            id="tooltip_ordem_edicoes_cc",)},
                    selected='0',
                ),
                ui.input_checkbox_group(
                    id="checkbox_areas_cc",
                    label="Escolher área:",
                    # list choices using dict_areas from 1-3 index
                    choices={chave: valor for chave, valor in dict_areas.items() if list(dict_areas.keys()).index(chave) > 0}, 
                    selected=list(dict_areas.keys()),
                ),
                ui.input_checkbox_group(
                    id="checkbox_questoes_cc",
                    label="Escolher tipos de questões:",
                    choices=dict_questoes, 
                    selected=list(dict_questoes.keys()),
                ),    
            ),
            ui.layout_columns(
                ui.value_box( 
                    "Simulados Realizados:", ui.output_ui("simulados_realizados_cc"), showcase=ICONS["book"]
                ),
                ui.value_box(
                    "Média do Número do Tipo de Questão:", ui.output_ui("media_tipo_questao"), showcase=ICONS["calculator"]
                ),
            fill=False,
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Dados"), ui.output_data_frame("cc_table"), full_screen=True
                ),
                ui.card(
                    ui.card_header(
                        "Número de Questões vs Edição",
                        class_="d-flex justify-content-between align-items-center",
                    ),
                    output_widget("plot_cc"),
                    full_screen=True,
                ),
                col_widths=[4, 8],
            ),
        ),
    ]

app_ui = ui.page_fluid(
    ui.tags.html(
        ui.h1({"style": "text-align: center;"}, "Análise de dados Simulados Enem"),
        ui.navset_card_tab(
            ui.nav_panel("Análise quantidade de acertos e melhoras", nav_acertos_melhoras()),
            ui.nav_panel("Análise conversão de conhecimento", nav_conversao_conhecimento()),
        ),
    ),
)

def server(input, output, session):

    # ======================================================================
    # ANÁLISE QUANTIDADE DE ACERTOS E MELHORAS (enem_acertos_melhoras.csv)
    # ======================================================================

    # ui used for comparing attempts
    @render.ui
    def secao_comparar_acertos():
        # checkbox acertos checked
        if input.checkbox_acertos() and input.radio_area() == '1':
            return ui.layout_columns(
                ui.value_box(
                    "Média de melhora", ui.output_ui("media_melhora"), showcase=ICONS["arrow-up"]
                ),
                ui.card(
                    ui.card_header(
                        "Diferença entre acertos da primeira tentativa vs segunda tentativa",
                        ui.popover(
                            ICONS["ellipsis"],
                            ui.input_radio_buttons(
                                "area_diff_acertos",
                                label='Escolha a área:',
                                choices=["media_todas_selecionadas", *list(input.checkbox_areas_am())],
                                selected="media_todas_selecionadas",
                                inline=True,
                            ),
                            title="Mude a área a ser analisada",
                            placement="top",
                        ),
                        class_="d-flex justify-content-between align-items-center",
                    ),
                    output_widget("plot_am_diff_acertos"),
                    full_screen=True,
                ),
                col_widths=[3, 9],
                
            ),    
        else:
            return ui.TagList()

    # gets the data from the acertos e melhoras (enem_acertos_melhoras.csv) section
    @reactive.calc
    def am_data():
        df_final = df_am
        df_final = df_final.sort_values('edicao')

        if input.radio_ordem_am() == '1': # == 'Ordem cronológica por resolução
            df_final = df_final.set_index('edicao')
            # df_cc 'edicao' is sorted for this case
            df_final = df_final.reindex(index=df_cc['edicao'])
            df_final = df_final.reset_index()

        if input.radio_area() == '0': # redação was choosen
            df_final = df_final[['edicao', 'redacao']]
            df_final = df_final.dropna(subset='redacao')
        else: # other areas were choosen
            # get the list of the choosen areas
            lista_areas_selecionadas = list(input.checkbox_areas_am())

            # separate the wished areas and handle with missing values
            if input.checkbox_acertos():
                colunas_melhora = [f'melhora_{area}' for area in lista_areas_selecionadas]
                df_final = df_final[['edicao'] + lista_areas_selecionadas + colunas_melhora]
                df_final = df_final.dropna(subset=colunas_melhora)
                df_final = df_final.dropna(subset=lista_areas_selecionadas)
                # normalize the melhoras columns
                for area in lista_areas_selecionadas:
                    # primeira_area is the number of correct answers I had in the first attempt at the simulated exam 
                    df_final[f'primeira_{area}'] = df_final[area] - df_final[f'melhora_{area}']
            else:
                df_final = df_final[['edicao'] + lista_areas_selecionadas]
                df_final = df_final.dropna(subset=lista_areas_selecionadas)

        return df_final

    # INFORMATION CARDS
    @render.ui
    def simulados_realizados():
        return am_data().shape[0]

    @render.ui
    def media_acertos_total():
        df_final = am_data()
        if input.radio_area() == '0': # redação was choosen
            string_final = f'{int(df_final["redacao"].mean())} / 1000'
        else: # other areas were choosen
            lista_areas_selecionadas = list(input.checkbox_areas_am())
            medias = 0
            for area in lista_areas_selecionadas:
                medias += int(df_final[area].mean())
            # 45 because was the number of questions of each area
            string_final = f'{int(medias)} / {len(lista_areas_selecionadas)*45}'

        return string_final

    @render.ui
    def media_acertos_area():
        df_final = am_data()
        if input.radio_area() == '0': # redação was choosen
            media = round(df_final["redacao"].mean())
            string_final = f'{media} / 1000'
        else: # other areas were choosen
            string_final = '<div style="font-size: 1rem;">'            
            lista_areas_selecionadas = list(input.checkbox_areas_am())
            
            for area in lista_areas_selecionadas:
                media = round(df_final[area].mean())
                string_final += f'{dict_areas[area]}: <strong>{media}</strong><br>'
                
        return ui.HTML(string_final)

    @render.ui
    def media_melhora():
        df_final = am_data()
        lista_areas_selecionadas = list(input.checkbox_areas_am())
        
        string_final = '<div style="font-size: 1rem;">'
        for area in lista_areas_selecionadas:
            string_area = f'melhora_{area}'
            # necessary verification to avoid errors arising from the loading delay of the secao_comparar_acertos()
            if string_area in df_final.columns: 
                media = round(df_final[string_area].mean())
                string_final += f'{dict_areas[area]}: <strong>{media}</strong><br>'
            else:
                string_final += f'{dict_areas[area]}: Dados não disponíveis<br>'
        
        string_final += '</div>'
        
        return ui.HTML(string_final)
    
    @render.data_frame
    def am_table():
        return render.DataGrid(am_data())
    
    @reactive.Effect
    @reactive.event(input.radio_area)
    # expand the options if redacao is not choosen
    def _():
        ui.update_navs("nav_radio_area", selected=input.radio_area())

    # PLOTS
    # build the plot for Acertos e Melhoras tab
    @render_plotly
    def plot_am():
        df_final = am_data()

        if input.radio_area() == '0':  # redação was choosen
            fig = px.line(df_final, x='edicao', y='redacao', markers=True, title='Redação')
            fig.update_yaxes(range=[760, 1010], tickvals=list(range(760, 1001, 40)), title='Pontuação')
        else:  # other areas were choosen
            fig = px.line()

            segunda_tentativa = ''
            for area in input.checkbox_areas_am():
                if input.checkbox_acertos():
                    fig.add_scatter(x=df_final['edicao'], y=df_final[f'primeira_{area}'], mode='lines+markers', name=f"{dict_areas[area]} 1ª tentativa")
                    segunda_tentativa = '2ª tentativa'
                fig.add_scatter(x=df_final['edicao'], y=df_final[area], mode='lines+markers', name=f"{dict_areas[area]} {segunda_tentativa}")

            fig.update_yaxes(range=[20, 45], tickvals=list(range(20, 46, 2)), title='Acertos')
            fig.update_xaxes(tickangle=55, title='Edição')
            fig.update_layout(xaxis_title='Edição', yaxis_title='Acertos', showlegend=True)
        
        return fig
    
    # build the plot for the 'Diferença entre acertos primeira vs segunda tentativa'
    @render_plotly
    def plot_am_diff_acertos():
        df_final = am_data()

        # Extracting only the columns for 'melhora'
        lista_areas_selecionadas = input.checkbox_areas_am()
        melhora_cols = [f'melhora_{area}' for area in lista_areas_selecionadas]
        
        df_melhora = pd.concat([df_final[['edicao']], df_final[melhora_cols]], axis=1)
        df_melhora['melhora_media_todas_selecionadas'] = df_melhora[melhora_cols].mean(axis=1)

        yvar = f'melhora_{input.area_diff_acertos()}'

        fig = px.bar(df_melhora, x='edicao', y=yvar, title=yvar)
        fig.update_layout(xaxis_title='Edição', yaxis_title='Média de Melhora', showlegend=False)
        
        return fig

    # ======================================================================
    # ANÁLISE CONVERSÃO DE CONHECIMENTO (enem_conversao_conhecimento.csv)
    # ======================================================================

    @render.ui
    def simulados_realizados_cc():
        return cc_data().shape[0]
    
    @render.ui
    def media_tipo_questao():
        df_final = cc_data()
        string_final = '<div style="font-size: 1rem;">'            
        lista_areas_selecionadas = list(input.checkbox_areas_cc())
        
        tipos_questoes_selecionados = list(input.checkbox_questoes_cc())
        for tipo_questao in tipos_questoes_selecionados:
            colunas_tipo_questao = [col for col in df_final.columns if col.endswith('_' + tipo_questao)]
            media = round(df_final[colunas_tipo_questao].stack().mean())
            string_final += f'{dict_questoes[tipo_questao]}: <strong>{media}</strong><br>'
            
        string_final += '</div>'
        
        return ui.HTML(string_final)
    
    @render.data_frame
    def cc_table():
        return cc_data()
    
    @reactive.Calc
    def cc_data():
        df_final = df_cc
        
        df_final = df_final.sort_values('edicao')

        if input.radio_ordem_cc() == '1': # == 'Ordem cronológica por resolução
            df_final = df_final.set_index('edicao')
            # df_cc 'edicao' is sorted for this case
            df_final = df_final.reindex(index=df_cc['edicao'])
            df_final = df_final.reset_index()

        # select the wanted columns and drop nan values
        colunas_selecionadas = []
        for area in list(input.checkbox_areas_cc()):
            # important prefix to individualize areas
            area_prefix = area[:3] 
            # select the columns for the choosen areas 
            colunas_area = [coluna for coluna in df_final.columns if coluna.startswith(area_prefix)]
            for tipo_questao in list(input.checkbox_questoes_cc()):
                # combine the selected areas with the type of question
                colunas_selecionadas.extend([coluna for coluna in colunas_area if coluna.endswith('_' + tipo_questao)])
        df_final = df_final[['edicao'] + colunas_selecionadas]
        df_final = df_final.dropna(subset=colunas_selecionadas)


        return df_final
        
    # build the plot for Conversão de Conhecimento tab
    @render_plotly
    def plot_cc():
        df_final = cc_data()

        # organize the data for the plot
        data = []
        for coluna in df_final.columns:
            if coluna != 'edicao':
                area, tipo_questao = coluna.split('_', 1) # separate area and tipo_questao from the columns names
                label = f"{dict_areas[area]} - {dict_questoes[tipo_questao]}"
                for edicao, valor in zip(df_final['edicao'], df_final[coluna]):
                    data.append({'Edição': edicao, 'Valor': valor, 'Legenda': label})

        # create plot using plotly
        df_plotly = pd.DataFrame(data)
        fig = px.line(df_plotly, x='Edição', y='Valor', color='Legenda', markers=True,
                    labels={'Edição': 'Edição', 'Valor': 'Questões', 'Legenda': 'Área e Tipo de Questão'})

        # adjust layout
        fig.update_layout(xaxis_title='Edição', yaxis_title='Questões',
                        legend_title='Área e Tipo de Questão', xaxis=dict(tickangle=55))

        return fig


app = App(app_ui, server)