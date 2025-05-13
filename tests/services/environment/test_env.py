from orionis.luminate.services.environment.env import Env, env
from orionis.luminate.test import TestCase
from orionis.framework import *

class TestDotEnv(TestCase):

    async def testDotEnv(self):

        # Test set and get environment variable.
        Env.set('NAME', NAME)
        result = Env.get('NAME')
        self.assertEqual(result, NAME)

        # Test unset environment variable.
        Env.set('VERSION', VERSION)
        Env.unset('VERSION')
        result = Env.get('VERSION')
        self.assertIsNone(result)

        # Test env helper function retrieves variable.
        Env.set('DOCS', DOCS)
        result = env('DOCS')
        self.assertEqual(result, DOCS)

        # Test retrieving all environment variables.
        Env.set('SKELETON', SKELETON)
        Env.set('FRAMEWORK', FRAMEWORK)
        result = Env.all()
        self.assertEqual(result.get('SKELETON'), SKELETON)
        self.assertEqual(result.get('FRAMEWORK'), FRAMEWORK)

        # Destroy the environment
        Env.destroy()