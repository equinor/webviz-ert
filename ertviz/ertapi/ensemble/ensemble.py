from ertviz.ertapi.ensemble.request_data import RequestData


class Ensemble(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)
