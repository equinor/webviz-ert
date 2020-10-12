from ertviz.ertapi.ensemble.request_data import RequestData, ParametersDict


class Realization(RequestData):
    def __init__(self, request_handler, metadata_dict):
        self._univariate_missfits = None
        self._summarized_missfits = None
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    def load_metadata(self):
        super().load_metadata()

        if "univariate_misfits" in self.metadata:
            self._univariate_missfits = self.metadata["univariate_misfits"]

        if "summarized_misfits" in self.metadata:
            self._summarized_missfits = self.metadata["summarized_misfits"]

    def univariate_misfits(self, obs_key):
        if obs_key in self._univariate_missfits:
            return self._univariate_missfits[obs_key]

    def summarized_misfits(self, obs_key):
        if obs_key in self._summarized_missfits:
            return self._summarized_missfits[obs_key]

    @property
    def parameters(self):
        return ParametersDict("parameters", "name", self)
