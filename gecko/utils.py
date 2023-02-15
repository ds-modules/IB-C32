from datascience import *
from IPython.display import *
from ipywidgets import *
import pandas as pd
import numpy as np
import plotly.express as px;
import scipy.constants as constant 
import math
from ipywidgets import *
import re
import json
from typing import *

def read(fp: str, full_fp: bool = False) -> dict:
    """
    ### Creates a dictionary of the given JSON file

    Parameters
    ----------
    fp : `str`
        The file path of the JSON file
        such that file is named `data/json/<fp>.json`

    full_fp : `bool`
        Whether the filepath is the full filepath or not

    Returns
    -------
    `dict`
        A dictionary of the JSON file

    Examples
    --------
    >>> read("example.json")
    {'a': 1, 'b': 2, 'c': 3}
    """
    if not full_fp:
        fp = f"{fp}.json"
    return json.load(open(fp, "r"))

def show(*args, tags = []):
    """Pretty Display"""
    assert (tags == []) or (type(tags[0]) == str), "tags must contain strings"
    for i in args:
        if type(i) != str:
            i = str(i)
        for tag in tags:
            i = f"<{tag}>{i}</{tag}>"
        display(Markdown(i))

def get_data() -> pd.DataFrame:
    """
    Get data from the Google Sheet and add the section column.
    
    Parameters
    ----------
    
    None
    
    Returns
    -------
    pd.DataFrame
        Data from the database with the section column.
    """
    df = fetch_data()
    df = add_section_column(df)
    df = rename_columns(df)
    return df

def fetch_data() -> pd.DataFrame:
    """
    Fetches data via google sheets from a fixed url.
    
    Parameters
    ----------
    
    None
    
    Returns
    -------
    
    data : pd.DataFrame
        The data from the google sheet
    """
    url = "https://docs.google.com/spreadsheets/d/1RH96Rjr_bC5bcpd3DqY5shsuEMtxlk4NN39pUYrGeNA/edit#gid=0"
    csv_url = re.sub("/edit#gid=", "/export?format=csv&gid=", url)
    data = pd.read_csv(csv_url)
    return data

def add_section_column(data : pd.DataFrame) -> pd.DataFrame:
    """
    Adds a column to the data that contains the section number.
    
    Parameters
    ----------
    
    data : pd.DataFrame
        The data from the google sheet
    
    Returns
    -------
    
    data : pd.DataFrame
        The data with the section column added and columns reordered.
    """
    section_dict = read("teams")
    section_from_team = lambda team: section_dict[str(team)]
    data["Section"] = data["Team"].apply(section_from_team)
    data = data[["Team", "Section", "Mass", "Angle", "ShearForce", "AdhesiveForce"]]
    return data

def rename_columns(data : pd.DataFrame) -> pd.DataFrame:
    """
    Renames the columns of the data to be more readable.
    
    Parameters
    ----------
    
    data : pd.DataFrame
        The data from the google sheet
    
    Returns
    -------
    
    data : pd.DataFrame
        The data with the columns renamed.
    """
    data = data.rename(columns={"Mass": "Mass (g)", "Angle": "Angle (degrees)", "ShearForce": "Shear Force (N)", "AdhesiveForce": "Adhesive Force (N)"})
    return data

def section_from_team(team : int) -> int:
    """ 
    Gets the section number for a given team.
    
    Parameters
    ----------
    
    team : int
        The team number to get the section for.
    
    Returns
    -------
    
    int : The section number for the given team.
    
    """
    sections = read("teams")
    return sections[str(team)]

def get_class_data(team : int, section : int) -> pd.DataFrame:
    df = get_data()
    groups = []
    for t, s in zip(df["Team"], df["Section"]):
        class_data = df[df["Section"] == section]
        if team == t:
            groups.append("My Team")
        elif s == section:
            groups.append("My Section")
        else:
            groups.append("Rest of Class")
    df["Group"] = groups
    return df
    
def enter_team_number():
    show("Select a team number to get data for.", tags=["h2"])
    show("You can also use the arrow keys to change the team number, or simply type it into the box.", tags=["blockquote", "h3"])
    w = BoundedIntText(value = None, min = 1, max = 35, step = 1, description = "Team:")
    display(w)
    return w

def get_info(w : widgets.widget_int.BoundedIntText) -> Tuple[int, int]:
    """
    Retrieves the team and section number from the widget.
    
    Parameters
    ----------
    
    w : widgets.widget_int.BoundedIntText
        The widget containing the team number.
    
    Returns
    -------
    
    tuple : A tuple containing the team number and section number.
    """
    team = w.value
    section = section_from_team(team)
    return (team, section)

def show_data(data : pd.DataFrame) -> None:
    section = data.query("Group == 'My Team'")["Section"].values[0]
    team = data.query("Group == 'My Team'")["Team"].values[0]
    data = data.copy().drop(columns=["Section", "Team"])
    show("Use the dropdown menu to select a group to view.", tags=["h2"])
    show("Then, use the slider to determine how many rows to show.", tags=["h3"])
    show("Note: You can also click the number next to the slider to change the number of rows.", tags=["blockquote", "h3"])
    show("Make sure you take a screenshot of the \"My Team\" table to submit!", tags=["h1", "center"])
    @interact(group = Dropdown(value = "My Team", options = data["Group"].unique()),
              rows = IntSlider(value = 10, min = 1, max = 60, step = 1),
              section = fixed(section),
              team = fixed(team))
    def helper(group, rows = 10, section = section, team = team):
        df = data[data["Group"] == group].reset_index(drop=True).drop(columns=["Group"])
        if group == "My Team":
            show(f"Team {team} Data", tags=["h2"])
        elif group == "My Section":
            show(f"Section {section} Other Teams Data", tags=["h2"])
        else:
            show("Rest of the Class Data", tags=["h2"])
        return df.head(rows)
 
def get_tables(widget) -> Tuple[int, int, pd.DataFrame]:
    """
    Gets the team number, section number, and data for the given widget.
    
    Parameters
    ----------
    
    widget : widgets.widget_int.BoundedIntText
        The widget containing the team number.
    
    Returns
    -------
    
    tuple : A tuple containing the team number, section number, and data.
    """
    team, section = get_info(widget)
    data = get_class_data(team, section)
    return (team, section, data)   

def plot_data(df):
    cols = ["Mass (g)", "Angle (degrees)", "Shear Force (N)", "Adhesive Force (N)"]
    show("Use the dropdown menu to select a column to plot on the x-axis and y-axis.", tags=["h2"])
    show("Make sure to save the graph as an image to submit!", tags=["h1", "center"])
    show("To do that, hover over the top right corner of the graph and click the camera button!", tags=["h2", "center"])
    @interact(x = Dropdown(value = "Mass (g)", options = cols),
              y = Dropdown(value = "Angle (degrees)", options = cols))
    def helper(x, y):
        title = f"{x} vs {y}"
        return px.scatter(df, x=x, y=y, color = "Group", template = "seaborn", title = title, width = 800, height = 800, trendline = "ols")


# All code below this line was written in Spring 22
# _____________________________________________________________________________
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
file = widgets.FileUpload(accept="*.csv", multiple=False)

def how_to_upload():
    show("Use the button `Upload` below to choose your data from your computer to upload into this notebook",
             "After uploading, ***run this cell one more time*** to save and display your data!",
            "It will be saved under the name `my_data`",
            "**If for any reason you messed up, add the following line to some new cell and run it,**",
            "then ensure you delete the line before running the cell again**",
            "<pre>redo = True</pre>")
def file_to_csv(file):
    if not file.value:
        how_to_upload()
        display(file)
    else:
        import io
        upload = list(file.value.items())[0][1]['content']
        content = Table.from_df(pd.read_csv(io.BytesIO(upload), sep=None, engine='python'))
        return content
    
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

# –––––––––––––––––––––––––––
#| For Visualization Section |
# –––––––––––––––––––––––––––

def visualize(data):
    @interact(Kind = widgets.Dropdown(options=["Scatter Plot", "Histogram"], value = None))
    def plot_kind(Kind):
        cols = widgets.Dropdown(options=data.labels)
        if Kind == "Scatter Plot":
            show(">***NOTE:*** If you chose `Color By` to be a column with numeric data, " \
                 + "that will **disable the `Side Graph`** parameter")
            @interact(x = widgets.Dropdown(options=data.labels, value = None, 
                                           description = "X-Axis"), 
                      y = widgets.Dropdown(options=data.labels, value = None, 
                                           description = "Y-Axis"),
                      color = widgets.Dropdown(options= [None] + list(data.labels), value = None, 
                                               description = "Color By"),
                     marginal = widgets.Dropdown(options = [None, 'rug', 'box', 'violin','histogram'], 
                                                 value = 'histogram', description = "Side Graph"))
            def scatter_helper(x, y, marginal, color):
                if color != None and data[color].dtype == float:
                    marginal = None
                if (x != None and y != None):
                    px.scatter(data_frame = data.to_df(), 
                               x = x, y = y, 
                               color = color,
                               color_continuous_scale='viridis', 
                               template = 'seaborn',
                               marginal_x = marginal, marginal_y = marginal,
                               title = f"{x} vs. {y}").show()
        if Kind == "Histogram":
            show("Using the `Color By` variable here leads to some odd displays",
                 "They aren't really usefull, but we've the option to se it in case you are curious",
                 "The default `None` gives a solid color")
            @interact(x = widgets.Dropdown(options=data.labels, value = None,
                                          description = "X-Axis"),
                      color = widgets.Dropdown(options=[None] + list(data.labels), value = None,
                                              description = "Color By"),
                     marginal = widgets.Dropdown(options = [None, 'rug', 'box', 'violin','histogram'], 
                                                 value = 'box', description = "Top Graph"))
            def hist_helper(x, marginal, color):
                if (x != None):
                    px.histogram(data_frame = data.to_df(), 
                               x = x,
                               color = color, template = "seaborn",
                                marginal = marginal,
                                title = f"Distribution of {x}").show()
