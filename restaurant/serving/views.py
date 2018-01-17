import random

from rest_framework import serializers, fields
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from serving.models import Server, SERVER_STATES


class BaseAPIView(APIView):
    METHOD_SERIALIZERS = {}
    params = {}

    def initial(self, request, *args, **kwargs):
        """
        Retrieve params from three places: url path, query string, and http body. Params in the url path are retrieved
        from the regex in the urls.py file. If we have not specified a serializer for the endpoint then do not perform
        any validation. Since the regex in the url performs some basic validation then don't bother rewriting the same
        logic.
        """
        self.params = kwargs
        method = request.method.lower()
        if method not in self.METHOD_SERIALIZERS.keys():
            print('could not find method. exiting early')
            return
        if method == 'get':
            request_data = request.query_params.copy()
        else:
            request_data = request.data.dict()
        request_data.update(kwargs)
        validated_data = self.METHOD_SERIALIZERS[method](data=request_data)
        if validated_data.is_valid(raise_exception=True):
            self.params.update(validated_data.validated_data)


class ServerCheckinView(BaseAPIView):

    class ServerUpdateStateSerializer(serializers.Serializer):
        server = fields.RegexField(regex=r'[a-fA-F0-9]{1,32}')
        state = fields.ChoiceField(choices=SERVER_STATES)

    METHOD_SERIALIZERS = {
        'post': ServerUpdateStateSerializer,
    }

    def get(self, request, *args, **kwargs):
        return Response({'server': self.params['server'], 'state': self.params.get('state', 'unknown')})

    def post(self, request, *args, **kwargs):
        """
        Change the working state of a server.
        """
        Server.objects.update_server(server_id=self.params['server'], state=self.params['state'])
        return Response({'success': True})


