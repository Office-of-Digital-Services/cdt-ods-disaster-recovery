from .models import UserFlow


def userflows(request):
    flows = []
    try:
        for flow in UserFlow.objects.all():
            flows.append({"label": flow.label, "index_url": flow.index_url})
    except Exception:
        pass

    return {"userflows": flows}
