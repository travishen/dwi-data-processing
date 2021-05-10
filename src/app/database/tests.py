import unittest

from . import _sessions


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.scoped_session = _sessions.get('default')
        self.session = self.scoped_session()

    def tearDown(self):
        self.session.rollback()
        # Remove it, so that the next test gets a new Session()
        self.scoped_session.remove()
