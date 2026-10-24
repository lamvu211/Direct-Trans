import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from process_util import iter_directtrans_pids


class TestProcessUtil(unittest.TestCase):
    def test_iter_directtrans_pids_parses_csv(self):
        stdout = (
            '"DirectTrans_v2.0.0.exe","100","Console","1","12,345 K"\n'
            '"chrome.exe","200","Console","1","50,000 K"\n'
            '"DirectTrans_v2.0.1.exe","300","Console","1","12,400 K"\n'
        )
        with patch("process_util.run_hidden") as run_hidden:
            run_hidden.return_value.stdout = stdout
            pids = iter_directtrans_pids(exclude_pid=300)
        self.assertEqual(pids, [100])

    def test_iter_directtrans_pids_excludes_current(self):
        stdout = '"DirectTrans.exe","42","Console","1","10 K"\n'
        with patch("process_util.run_hidden") as run_hidden:
            run_hidden.return_value.stdout = stdout
            pids = iter_directtrans_pids(exclude_pid=42)
        self.assertEqual(pids, [])


if __name__ == "__main__":
    unittest.main()
