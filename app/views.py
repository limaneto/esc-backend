from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def hello_world(request):
    return Response({"message": "Got some data!", "data": request.data})
