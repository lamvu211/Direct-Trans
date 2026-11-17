import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from constants import NVIDIA_DEFAULT_MODEL
from nvidia_models import list_nvidia_model_choices


class TestNvidiaModels(unittest.TestCase):
    def test_static_model_list(self):
        choices = list_nvidia_model_choices()
        self.assertEqual(choices, [NVIDIA_DEFAULT_MODEL])
        self.assertEqual(NVIDIA_DEFAULT_MODEL, "nvidia/nemotron-3.5-bolt-e4b")


if __name__ == "__main__":
    unittest.main()