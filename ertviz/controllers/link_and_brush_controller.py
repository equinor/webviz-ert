import dash
from dash.dependencies import Input, Output, ALL
from dash.exceptions import PreventUpdate


def _parse_response_selection(selectedData, ensemble_plot):
    if selectedData:
        plot_idxs = set([p["curveNumber"] for p in selectedData["points"]])
        real_idxs = [
            ensemble_plot.plot_ids[p] for p in plot_idxs if p in ensemble_plot.plot_ids
        ]
        return list(real_idxs)


def _parse_parameter_selection(selectedData, parameter_plot):
    if selectedData:
        if "pointNumbers" in selectedData["points"][0]:
            plot_idxs = []
            for selection in selectedData["points"]:
                plot_idxs += selection["pointNumbers"]
        else:
            plot_idxs = set([p["pointNumber"] for p in selectedData["points"]])
        real_idxs = [
            parameter_plot.plot_ids[p]
            for p in plot_idxs
            if p in parameter_plot.plot_ids
        ]
        return real_idxs


def link_and_brush_controller(parent, app):
    @app.callback(
        Output(parent.uuid("selection-store"), "data"),
        [Input({"id": ALL, "type": parent.uuid("graph")}, "selectedData")],
    )
    def graph_selection(selectedData):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        else:
            graph_id = ctx.triggered[0]["prop_id"]

        # Get models from somewhere more generic
        # use type for switching between
        if "response" in graph_id:
            return _parse_response_selection(ctx.inputs[graph_id], parent.ensemble_plot)
        if "parameter" in graph_id:
            return _parse_parameter_selection(
                ctx.inputs[graph_id], parent.parameter_plot
            )
