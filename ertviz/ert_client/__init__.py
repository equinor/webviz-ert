from ertviz.models import Response, EnsembleModel


def get_response(ref_url):
    return Response(ref_url=ref_url)

def get_ensemble(ref_url):
    return EnsembleModel(ref_url=ref_url)