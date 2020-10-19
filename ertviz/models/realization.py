from ertviz.data_loader import get_data


class Realization:
    def __init__(self, realization_schema):
        self._name = realization_schema["name"]
        self._data_url = realization_schema["data_url"]
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = get_data(self._data_url)
        return self._data

    @property
    def name(self):
        return self._name
