from django.http import HttpResponse
import datetime


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>Currently is now %s.</body></html>" % now
    return HttpResponse(html)
