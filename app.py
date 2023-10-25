import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import pandas as pd
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

# am for acertos e melhoras
df_am = pd.read_csv("enem_acertos_melhoras.csv")
# cc for conversao de conhecimento
df_cc = pd.read_csv("enem_conversao_conhecimento.csv")

dict_areas = {
    # name          # beuaty name            # color
    'linguagens':   ['Linguagens',          'tab:red'],
    'humanas':      ['Ciências Humanas',    'tab:orange'],
    'matematica':   ['Matemática',          'tab:purple'],
    'natureza':     ['Ciências da Natureza','tab:green'],
}

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

dict_questoes = {
    's': 'Questões que eu sabia',
    's_e':  'Questões que sabia e errei',
    'ns': 'Questões que eu não sabia',
    'ns_e': 'Questões que eu não sabia e errei',
}

# given color and factor, darken this color with this factor
def darken_color(cor, fator):
    color_rgb = mcolors.to_rgb(cor)
    new_color_rgb = tuple(comp * (1 - fator) for comp in color_rgb)
    new_color = mcolors.to_hex(new_color_rgb)
    return new_color

# show the checkbox_areas_am if 'Escolher área(s)' is pressed in radio_areas
# in acertos e melhora tab
def show_checkbox_areas():
    return [
        ui.input_checkbox_group(
            id="checkbox_areas_am",
            label="Escolher análise:",
            choices={chave: valor[0] for chave, valor in dict_areas.items()},
            selected=list(dict_areas.keys()),
        ),
        ui.input_checkbox(
            id="checkbox_acertos", 
            label="Comparar acertos da primeira tentativa", 
            value=False,
        ),

    ]

# nav that show acertos e melhoras related to df_am
def nav_acertos_melhoras():
    return [
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_radio_buttons(
                    id="radio_ordem_am", 
                    label="Ordem das edições:", 
                    choices={'0': "Alfabética", '1': "Cronológica por resolução"},
                    selected='0',
                ),
                ui.input_radio_buttons(
                    id="radio_area", 
                    label="Área:", 
                    choices={'0': "Redação", '1': "Escolher área(s)"},
                    selected='1',
                ),
                ui.navset_hidden(
                    ui.nav(None, "", value='0'),
                    ui.nav(None, show_checkbox_areas(), value='1'),
                    id="nav_radio_area",
                ),    
            ),
            ui.panel_main(
                ui.output_plot("plot_am"),
                # TOOO
                # add details about the plot
            ),
        ),
    ]

# nav that show conversao de conhecimento related to df_cc
def nav_conversao_conhecimento():
    return [
        # TODO
        # explain ling and context
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_radio_buttons(
                    id="radio_ordem_cc", 
                    label="Ordem das edições:", 
                    choices={'0': "Alfabética", '1': "Cronológica por resolução"},
                    selected='0',
                ), 
                ui.input_checkbox_group(
                    id="checkbox_areas_cc",
                    label="Escolher área:",
                    # list choices using dict_areas from 1-3 index
                    choices={chave: valor[0] for chave, valor in dict_areas.items() if list(dict_areas.keys()).index(chave) > 0}, 
                    selected=list(dict_areas.keys()),
                ),
                ui.input_checkbox_group(
                    id="checkbox_questoes_cc",
                    label="Escolher tipos de questões:",
                    choices=dict_questoes, 
                    selected=list(dict_questoes.keys()),
                ),    

            ),
            ui.panel_main(
                ui.output_plot("plot_cc"),
                # TODO
                # add details like acertos de questoes que eu nao sabia
            ),
        ),

    ]

app_ui = ui.page_fluid(
    # TODO
    # add title
    # add context about everything
    ui.navset_tab_card(
        ui.nav("Análise quantidade de acertos e melhoras", nav_acertos_melhoras()),
        ui.nav("Análise conversão de conhecimento", nav_conversao_conhecimento()),
    ),
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.radio_area)
    # expand the options if redacao is not choosen
    def _():
        ui.update_navs("nav_radio_area", selected=input.radio_area())

    # build the plot for Acertos e Melhoras tab
    def build_plot_am():
        fig, ax = plt.subplots()
        
        result = df_am
        result = result.sort_values('edicao')

        if input.radio_ordem_am() == '1': # == 'Ordem cronológica por resolução
            result = result.set_index('edicao')
            # df_cc 'edicao' is sorted for this case
            result = result.reindex(index=df_cc['edicao'])
            result = result.reset_index()

        if input.radio_area() == '0': # redação was choosen
            result = result[['edicao', 'redacao']]
            result = result.dropna(subset='redacao')
            x = result['edicao']
            y = result['redacao']

            ax.set_yticks(range(760, 1001, 40))
            ax.set_ylabel('pontuacao')
            ax.plot(x, y, label='Redação', marker='o')

        else: # other areas were choosen
            # get the list of the choosen areas
            lista_areas_selecionadas = list(input.checkbox_areas_am())

            # separate the wished areas and handle with missing values
            if input.checkbox_acertos():
                colunas_melhora = [f'melhora_{area}' for area in lista_areas_selecionadas]
                result = result[['edicao'] + lista_areas_selecionadas + colunas_melhora]
                result = result.dropna(subset=colunas_melhora)
                result = result.dropna(subset=lista_areas_selecionadas)
                # normalize the melhoras columns
                for area in lista_areas_selecionadas:
                    # primeira_area is the number of correct answers I had in the first attempt at the simulated exam 
                    result[f'primeira_{area}'] = result[area] - result[f'melhora_{area}']
            else:
                result = result[['edicao'] + lista_areas_selecionadas]
                result = result.dropna(subset=lista_areas_selecionadas)

            # organize the plots
            for area in input.checkbox_areas_am():
                x = result['edicao']
                y1 = result[area]
                last_try_label = dict_areas[area][0]
                last_try_color = dict_areas[area][1]

                # plot the first try
                if input.checkbox_acertos():
                    y2 = result[f'primeira_{area}']
                    fst_try_label = last_try_label + ' 1ª tentativa'
                    fst_try_color = darken_color(last_try_color, 0.3)
                    ax.plot(x, y2, label=fst_try_label, color=fst_try_color, marker='o')
                    
                    # format the last try label (view purposes)
                    last_try_label += ' 2ª tentativa'
                
                # plot the last try
                ax.plot(x, y1, label=last_try_label, color=dict_areas[area][1], marker='o')

                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

            # local params for area plot
            ax.set_ylabel('acertos')
            ax.set_yticks(range(20, 46, 2))
            ax.set_aspect(0.2)
        
        # global params for every plot
        ax.tick_params(axis='x', labelrotation=55, bottom=True)
        ax.grid(axis='both', color='0.75')
        ax.set_title('titulo')        
        ax.set_xlabel('edicao')

        return fig
    
    # build the plot for Conversão de Conhecimento tab
    def build_plot_cc():
        fig, ax = plt.subplots()

        result = df_cc
        
        if input.radio_ordem_cc() == '0':
            result = result.set_index('edicao')
            result = result.sort_index()

        # select the wanted columns and drop nan values
        colunas_selecionadas = []
        for area in list(input.checkbox_areas_cc()):
            # important prefix to individualize areas
            area_prefix = area[:3] 
            # select the columns for the choosen areas 
            colunas_area = [coluna for coluna in result.columns if coluna.startswith(area_prefix)]
            # remove rows with nan values
            result = result.dropna(subset=colunas_area)

            for tipo_questao in list(input.checkbox_questoes_cc()):
                # combine the selected areas with the type of question
                # result the final columns to plot
                colunas_selecionadas.append(coluna for coluna in colunas_area if coluna.endswith('_' + tipo_questao)) # modify generator
        
        x = result.index # result['edicao']
        for coluna in colunas_selecionadas:
            y = result[coluna] 
            ax.plot(x, y, marker='o')  

            


        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
        ax.set_ylabel('questões')
        ax.set_yticks(range(20, 46, 2)) # modify later min and max
        ax.set_aspect(0.2)

        ax.tick_params(axis='x', labelrotation=55, bottom=True)
        ax.grid(axis='both', color='0.75')
        ax.set_title('titulo')        
        ax.set_xlabel('edicao')      

        return fig

    @output
    @render.plot
    def plot_am():
        build_plot_am()

    @output
    @render.plot
    def plot_cc():
        build_plot_cc()

app = App(app_ui, server)