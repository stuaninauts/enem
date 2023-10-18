import matplotlib.pyplot as plt
import pandas as pd
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

df = pd.read_csv("enem_acertos_melhoras.csv")

dict_areas = {
    'linguagens': 'Linguagens',
    'humanas': 'Ciências Humanas',
    'matematica': 'Matemática',
    'natureza': 'Ciências da Natureza'
}

# show the checkbox_areas if 'Escolher área(s)' is pressed in radio_areas
def show_checkbox_areas():
    return [
        ui.input_checkbox_group(
            id="checkbox_areas",
            label="Áreas:",
            choices=dict_areas,
            selected=list(dict_areas.keys()),
        ),
    ]

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
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
            ui.output_plot("plot"),
        ),
    ),
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.radio_area)
    def _():
        ui.update_navs("nav_radio_area", selected=input.radio_area())

    def build_plot():
        fig, ax = plt.subplots()
        result = df

        if input.radio_area() == '0': # Redação is choosed
            result = result[['edicao', 'redacao']]
            result = result.dropna(subset='redacao')
            x = result['edicao']
            y = result['redacao']
            ax.plot(x, y, label='Redação', marker='o')

            ax.set_yticks(range(720, 1001, 40))
            ax.set_ylabel('pontuacao')

        else: # Other areas are choosed
            lista_areas_selecionadas = list(input.checkbox_areas())
            colunas_melhora = [f'melhora_{area}' for area in lista_areas_selecionadas]
            result = result[['edicao'] + lista_areas_selecionadas + colunas_melhora]
            result = result.dropna(subset=lista_areas_selecionadas)

            for area in input.checkbox_areas():
                x = result['edicao']
                y = result[area]
                ax.plot(x, y, label=dict_areas[area], marker='o')

            ax.set_ylabel('acertos')
            ax.set_yticks(range(20, 46, 2))
            ax.set_aspect(0.2)
        
        ax.tick_params(axis='x', labelrotation=55, bottom=True)
        ax.grid(axis='both', color='0.75')
        ax.set_title('titulo')        
        ax.set_xlabel('edicao')

        return fig
    
    @output
    @render.plot
    def plot():
        build_plot()

app = App(app_ui, server)