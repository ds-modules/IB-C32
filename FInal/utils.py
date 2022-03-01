from datascience import *
from IPython.display import *
from ipywidgets import *
import pandas as pd
import numpy as np
import plotly.express as px;
import scipy.constants as constant
import math
from ipywidgets import *

def show(*args, tags = []):
    """Pretty Display"""
    assert (tags == []) or (type(tags[0]) == str), "tags must contain strings"
    for i in args:
        if type(i) != str:
            i = str(i)
        for tag in tags:
            i = f"<{tag}>{i}</{tag}>"
        display(Markdown(i))
        
# ––––––––––––––––––––––
#| For Formulas Section |
# ––––––––––––––––––––––



def forces_plot():
    show('>***Tip***: Hover your mouse over the line to see the points!',
         "The graph may take a second to update after you release the slider",
         " ",
         "Changing `m` will change the magnitude",
         "Changing `r` will change the amount of points that are plotted.")
    @interact(m = widgets.FloatSlider(min=0, max=10, 
                                      step=.05, value=4),
              r = widgets.FloatSlider(min=0, max=1,
                                      step=.1, value=.1),
             continuous_update=False)
    def both(m, r):
        '''Graph Adhesive vs. Shear Force'''

        def shear(m, a):
            '''Calculate Shear Force'''
            force_from_gravity = constant.g * m
            angled = np.array([math.cos(i) for i in a])
            return force_from_gravity * angled

        def adhesive(m, a):
            '''Calculate Adhesive Force'''
            force_from_gravity = constant.g * m
            angled = np.array([math.sin(i) for i in a])
            return force_from_gravity * angled

        x = np.arange(0, 100, r)
        sh, ad = shear(m, x), adhesive(m, x)
        graph = px.line(x = sh, y = ad, 
                        width = 500, height = 500, 
                        color_discrete_sequence = ["#003262"],
                        labels={"x": 'Shear Force (N)',
                                "y": "Adhesive Force (N)"})
        graph.update_xaxes(range=(0, 100))
        graph.update_yaxes(range=(0, 100))
        graph.show()


# –––––––––––––––––––––––––––––
#| For Data Background Section |
# –––––––––––––––––––––––––––––

cleaner = lambda x: x.replace("Sp", "Spring ")
class_data = Table.from_df(pd.read_excel("https://tinyurl.com/geck-data", sheet_name="Class"))
class_data["Collected"] = class_data.apply(cleaner, "Collected")
section_data = Table.from_df(pd.read_excel("https://tinyurl.com/geck-data", sheet_name="Sections"))


def show_gecko_tables():
    show("""
_**NOTE:**_ 
- To show ***ALL*** data, click the orange button
    - Click it again to reset
- Use the first dropdown box to choose what filter you'd like to use 
- Use the second box to chose what value you'd like to look for using the selected filter 
- Use the slider to pick how many rows of the table to show""") #instructions
    display(Markdown(" ")) #newline seperator
    @interact(show_all = widgets.ToggleButton(value=False, 
                                              description='Show ALL Tables', 
                                              icon = "eye", button_style = "warning"),
              Filter = widgets.Dropdown(options = ["Term", "Section", "Team"]))
    def view_gecko_data(show_all, Filter):
        def show_gecko(tab, Rows):
            error = f"<pre>Asked to display {Rows}"\
            + f" rows, but only {tab.num_rows} exist."\
            + f" Showing {tab.num_rows} rows</pre>"
            if Rows > tab.num_rows:
                display(Markdown(error))
                tab.show()
            else:
                tab.show(Rows)
                
        if show_all:
            display(Markdown("<pre>All Class Data:"))
            class_data.show()
            display(Markdown("<pre>All Section Data:"))
            section_data.show()
            return
        

        elif Filter == "Term":
            @interact(Term = widgets.Dropdown(options = ["Spring 2020", "Spring 2021"]),
                      Rows = widgets.IntSlider(min = 1, max = 300, value = 5))
            def show_class(Term, Rows):
                tab = class_data.where("Collected", Term)
                show_gecko(tab, Rows)

        elif Filter == "Section":
            @interact(Section = widgets.Dropdown(options = range(1, 7)),
                      Rows = widgets.IntSlider(min = 1, max = 50, value = 5))
            def show_section(Section, Rows):
                tab = section_data.where("Section", Section)
                show_gecko(tab, Rows)

        else:
            @interact(Team = widgets.Dropdown(
                options = [i for i in list(range(3, 37)) if i in np.unique(section_data["Team"])]),
                      Rows = widgets.IntSlider(min = 1, max = 10, value = 3))
            def show_section(Team, Rows):
                tab = section_data.where("Team", Team)
                show_gecko(tab, Rows)

def show_rows(self):
    display(Markdown("<pre>Use the slider below to select how many rows to show<pre>"))
    @interact(Rows = widgets.IntSlider(min = 1, max = self.num_rows, value = 5))
    def helper(Rows):
        self.show(Rows)
        
Table.show_interact = show_rows
