from ertviz.ertapi.ensemble import RequestData, Ensemble
from ertviz.ertapi.client.request_handler import RequestHandler


class Ensembles(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)
        self._ensembles = {}

    def __getitem__(self, ens_id):
        return self._get_ensemble_by_id(ens_id)

    def __iter___(self):
        return self._ensembles

    def __len__(self):
        return len(self._ensembles)

    def _get_ensemble_by_id(self, ens_id):
        if not ens_id in self._ensembles:
            self._ensembles[ens_id] = Ensemble(
                request_handler=self._request_handler,
                metadata_dict=self.metadata["ensembles"][ens_id],
            )
        return self._ensembles[ens_id]

    @property
    def names(self):
        return self.get_node_fields("ensembles", key="name").name

    @property
    def times_created(self):
        return self.get_node_fields("ensembles", key="time_created").time_created
