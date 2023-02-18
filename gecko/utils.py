from IPython.display import *
from ipywidgets import *
import pandas as pd
import plotly.express as px
import re
import json
from typing import *


class Instructions:

    def index(fn) -> Callable:
        if fn == "enter_team_number":
            return Instructions.team
        elif fn == "show_data":
            return Instructions.data
        elif fn == "plot_data":
            return Instructions.plot
        else:
            print("No instructions found for this function.")

    def team() -> None:
        show("Select a team number to get data for.", tags=["h2"])
        show("You can also use the arrow keys to change the team number, or simply type it into the box.", tags=[
             "blockquote", "h3"])

    def data() -> None:
        show("Make sure you take a screenshot of the \"My Team\" (below table) table to submit with your report!", tags=[
             "h1", "center"])
        explain = [
            "Notice that <code>group</code> has a dropdown menu that includes \"My Team\", \"My Section\", and \"Entire Class\".",
            "Data from experiments can be really noisy, \
            and it can be hard to see the trends that you're interested in without a lot of data points.",
            "For the next part of the notebook, \
            we're going to use the entire class's data to determine if the GSAs we synthesized function similarly to the toes of live geckos.",
            "Feel free to toggle the <code>group</code> menu to see data from other teams in your section and the rest of the class!"
        ]
        show(explain)

    def plot() -> None:
        mapper = {
            "Make sure to save the graph as an image to submit!": ["h1", "center"],
            "To do that, hover over the top right corner of the graph and click the camera button!": ["h2", "center"]
        }
        show(map=mapper)


def show_instructions(func: Callable) -> Callable:
    fn = name(func)
    instruct = Instructions.index(fn)

    def inner(*args, **kwargs):
        instruct()
        return func(*args, **kwargs)
    return inner


def name(func: Callable) -> str:
    assert isinstance(func, Callable), "Input must be callable."
    return func.__name__


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


def show(*args, tags: list = [], map: dict = None) -> None:
    """Pretty Display"""
    assert (tags == []) or (isinstance(tags[0], str)
                            ), "tags must contain strings"
    if map:
        for s, tags in map.items():
            show(s, tags=tags)
        return
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


def add_section_column(data: pd.DataFrame) -> pd.DataFrame:
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
    def section_from_team(team): return section_dict[str(team)]
    data["Section"] = data["Team"].apply(section_from_team)
    data = data[["Team", "Section", "Mass",
                 "Angle", "ShearForce", "AdhesiveForce"]]
    return data


def rename_columns(data: pd.DataFrame) -> pd.DataFrame:
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
    data = data.rename(columns={"Mass": "Mass (g)", "Angle": "Angle (degrees)",
                       "ShearForce": "Shear Force (N)", "AdhesiveForce": "Adhesive Force (N)"})
    return data


def section_from_team(team: int) -> int:
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


def get_class_data(team: int, section: int) -> pd.DataFrame:
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


@show_instructions
def enter_team_number() -> widget:
    w = BoundedIntText(value=None, min=1, max=35, step=1, description="Team:")
    display(w)
    return w


def get_info(w: widget) -> Tuple[int, int]:
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


@show_instructions
def show_data(data: pd.DataFrame) -> None:
    section = data.query("Group == 'My Team'")["Section"].values[0]
    team = data.query("Group == 'My Team'")["Team"].values[0]
    data = data.copy().drop(columns=["Section", "Team"])

    @interact(group=Dropdown(value="My Team", options=["My Team", "My Section", "Rest of Class"]),
              rows=IntSlider(value=10, min=1, max=60, step=1),
              section=fixed(section),
              team=fixed(team))
    def helper(group, rows=10, section=section, team=team):
        df = data[data["Group"] == group].reset_index(
            drop=True).drop(columns=["Group"])
        if group == "My Team":
            show(f"Team {team} Data", tags=["h2"])
        elif group == "My Section":
            show(f"Section {section} Other Teams Data", tags=["h2"])
        else:
            show("Rest of the Class Data", tags=["h2"])
        return df.head(rows)


def get_tables(widget: widget) -> Tuple[int, int, pd.DataFrame]:
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


def explore_data(df) -> None:
    cols = ["Mass (g)", "Angle (degrees)",
            "Shear Force (N)", "Adhesive Force (N)"]

    @interact(x=Dropdown(value="Mass (g)", options=cols),
              y=Dropdown(value="Angle (degrees)", options=cols),
              lines=Checkbox(value=False, description="Show Trend Lines")
              )
    def helper(x, y, lines):
        title = f"{x} vs {y}"
        if lines:
            return px.scatter(df, x=x, y=y, color="Group", template="seaborn", title=title, width=800, height=800, trendline="ols")
        else:
            return px.scatter(df, x=x, y=y, color="Group", template="seaborn", title=title, width=800, height=800)


@show_instructions
def plot_data(df) -> None:
    shear = r"\text{Shear Force} \ (F_{\parallel})"
    adhesive = r"\text{Adhesive Force} \ (F_{\perp})"
    vs = r"\ \text{vs.} \ "
    main = fr"$ {shear}{vs}{adhesive} $"

    fig = px.scatter(
        df,
        x="Shear Force (N)",
        y="Adhesive Force (N)",
        title=main,
        template="seaborn",
        width=800,
        height=600,
        labels={
            "Shear Force (N)": f"$ {shear} $",
            "Adhesive Force (N)": f"$ {adhesive} $"
        }
    )
    return fig


def feedback_button() -> None:
    button = '''
    <style>
    .button {
        border: 0;
        padding: 16px 32px 16px 32px;
        text-align: center;
        font-size: 18px;
        display: flex;
        transition: color 5s, 
                    background 5s, 
                    box-shadow 1s ease-out;
        cursor: pointer;
        color: #003262;
        border-radius: 30px;
        margin: 10% auto;
        background: linear-gradient(145deg, #e2e2e2, #bebebe);
        box-shadow: 20px 20px 40px 10px #afafaf, 
                    -20px -20px 40px 10px #f7f7f7, 
                    inset 0 0 0px, 
                    inset 0 0 0px;
    }
    
    .button:hover {
        color: #D3D3D3;
        background: #003262;
        box-shadow: 0 0 0px #000000, 
                    0 0 0px #000000, 
                    inset 20px 20px 40px 10px #002a51, 
                    inset -20px -20px 40px 10px #003b73;
    }
    </style>

    <a href="https://forms.gle/hipxf2uFw5Ud4Hyn8">
        <button class="button">
            Fill out the feedback form here
        </button>
    </a>
    '''
    display(HTML(button))
