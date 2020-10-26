from ertviz.models import Response, EnsembleModel


def get_response(name, ref_url):
    return Response(name, ref_url=ref_url)


def get_ensemble(ref_url):
    return EnsembleModel(ref_url=ref_url)
