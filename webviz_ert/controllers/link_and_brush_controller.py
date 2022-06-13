from dash import dcc
from typing import List, Dict, Union, Optional
from dash.dependencies import Input, Output, ALL
from dash.exceptions import PreventUpdate


def _parse_response_selection(
    selectedData: Optional[Dict], ensemble_plot: dcc.Graph
) -> List[int]:
    if selectedData:
        plot_idxs = set([p["curveNumber"] for p in selectedData["points"]])
        real_idxs = [
            ensemble_plot.plot_ids[p] for p in plot_idxs if p in ensemble_plot.plot_ids
        ]
        return real_idxs
    return []


def _parse_parameter_selection(
    selectedData: Optional[Dict], parameter_plot: dcc.Graph
) -> List[int]:
    if selectedData:
        if "pointNumbers" in selectedData["points"][0]:
            plot_idxs = []
            for selection in selectedData["points"]:
                plot_idxs += selection["pointNumbers"]
        else:
            plot_idxs = list(set([p["pointNumber"] for p in selectedData["points"]]))
        real_idxs = [
            parameter_plot.plot_ids[p]
            for p in plot_idxs
            if p in parameter_plot.plot_ids
        ]
        return real_idxs
    return []
