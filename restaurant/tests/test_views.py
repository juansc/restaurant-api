import pytest
from django.test import TestCase

from serving.models import Server


def assert_200_response(res):
    assert res.status_code == 200


def assert_json_response(res, expected_dict):
    assert res.json() == expected_dict


class ServerViewsTestCase(TestCase):
    def test_update_server_state_response(self):
        Server.objects.create(server_id='A' * 16, name='Julieta', state='on_break')
        res = self.client.post('/v1/server/{}/'.format('A'*16), data={'state': 'not_working'})
        print(res.json())
        assert_200_response(res)
        assert_json_response(res, {'success': True})


    def test_get_server_state(self):
        Server.objects.create(server_id='A' * 16, name='Julieta', state='on_break')
        res = self.client.get('/v1/server/{}/'.format('A'*16))
        assert_200_response(res)
        assert_json_response(res, {'server': 'A'*16, 'state': 'unknown'})
