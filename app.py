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

def show_checkbox_areas():
    return [
        ui.input_checkbox_group(
            id="checkbox_areas",
            label="Áreas:",
            choices=dict_areas,
            selected=dict_areas,
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
        colunas_melhora = [f'melhora_{area}' for area in list(input.checkbox_areas())]
        result = df[['edicao'] + list(input.checkbox_areas()) + colunas_melhora]
        print(result)
            
        for area in input.checkbox_areas():
            if area == 'matemática':
                area = 'matematica'

            x = result['edicao']
            y = result[area]
            ax.plot(x, y, label='area')

        return fig
    
    @output
    @render.plot
    def plot():
        build_plot()

app = App(app_ui, server)