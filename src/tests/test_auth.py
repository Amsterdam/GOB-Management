from unittest import TestCase, mock

from gobmanagement import auth



class TestAuth(TestCase):

    def setUp(self) -> None:
        pass

    @mock.patch("gobmanagement.auth.request")
    def testRequestUser(self, mocked_request):
        mocked_request.headers = {}
        request_user = auth.RequestUser()
        self.assertEqual(request_user._props, {})
        self.assertEqual(str(request_user), "USER: ")

        mocked_request.headers = {
            "X-Auth-prop1": "prop1 value",
            "X-Auth-prop2": "prop2 value",
            "X-prop3": "prop3 value",
        }
        request_user = auth.RequestUser()
        self.assertEqual(request_user._props, {
            'prop1': 'prop1 value',
            'prop2': 'prop2 value'
        })
        self.assertEqual(request_user.prop1, 'prop1 value')
        self.assertEqual(request_user.prop2, 'prop2 value')
        self.assertEqual(str(request_user), "USER: prop1='prop1 value', prop2='prop2 value'")
