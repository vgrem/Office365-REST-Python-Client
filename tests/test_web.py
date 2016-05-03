import unittest

from client.auth.authentication_context import AuthenticationContext
from client.client_context import ClientContext
from settings import settings


class MyTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MyTestCase, self).__init__(*args, **kwargs)
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['username'], password=settings['password'])
        self.context = ClientContext(settings['url'], ctx_auth)

    def test_load_web(self):
        cur_web = self.context.web
        self.context.load(cur_web)
        self.context.execute_query()
        self.assertIsNotNone(cur_web, "Web resource was not requested")

    def test_update_web(self):
        cur_web = self.context.web
        properties_to_update = {'Title': "New web site"}
        cur_web.update(properties_to_update)
        cur_web.context.execute_query()

        updated_web = self.context.web
        self.context.load(updated_web)
        self.context.execute_query()
        self.assertEquals(properties_to_update['Title'], updated_web.properties['Title'], "Web site update error")


if __name__ == '__main__':
    unittest.main()
