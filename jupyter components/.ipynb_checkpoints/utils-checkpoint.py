from Background import *
from datascience import *
from IPython.display import *
from ipywidgets import *
import pandas as pd
import numpy as np

cleaner = lambda x: x.replace("Sp", "Spring ")
class_data = Table.from_df(pd.read_excel("Background/Data/gecko.xlsx", sheet_name="Class"))
class_data["Collected"] = class_data.apply(cleaner, "Collected")
section_data = Table.from_df(pd.read_excel("Background/Data/gecko.xlsx", sheet_name="Sections"))

def show_gecko_tables():
    display(Markdown("""
_**NOTE:**_ 
- To show ***ALL*** data, click the orange button
    - Click it again to reset
- Use the first dropdown box to choose what filter you'd like to use 
- Use the second box to chose what value you'd like to look for using the selected filter 
- Use the slider to pick how many rows of the table to show""")) #instructions
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