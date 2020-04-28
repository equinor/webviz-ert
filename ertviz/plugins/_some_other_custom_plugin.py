from uuid import uuid4

import dash_html_components as html
from dash.dependencies import Input, Output
from webviz_config import WebvizPluginABC


class SomeOtherCustomPlugin(WebvizPluginABC):
    def __init__(self, app):

        super().__init__()

        self.button_id = f"submit-button-{uuid4()}"
        self.div_id = f"output-state-{uuid4()}"

        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(
            [
                html.H1("This is a static title"),
                html.Button(id=self.button_id, n_clicks=0, children="Submit"),
                html.Div(id=self.div_id),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            Output(self.div_id, "children"), [Input(self.button_id, "n_clicks")]
        )
        def _update_output(n_clicks):
            return f"Button has been pressed {n_clicks} times."
