from ertviz.ertapi.ensemble.request_data import RequestData


class Axis(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)


class Response(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    def load_metadata(self):
        super().load_metadata()

        self._axis = Axis(
            request_handler=self._request_handler, metadata_dict=self.metadata["axis"]
        )

    @property
    def axis(self):
        return self._axis
