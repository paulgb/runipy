
import unittest
from glob import glob
from os import path

from IPython.nbformat.current import read

from runipy.notebook_runner import NotebookRunner

class TestRunipy(unittest.TestCase):
    maxDiff = None
    def assert_notebooks_equal(self, expected, actual):
        self.assertEquals(len(expected['worksheets'][0]['cells']), len(actual['worksheets'][0]['cells']))
        for expected_out, actual_out in zip(expected['worksheets'][0]['cells'],
                actual['worksheets'][0]['cells']):
            self.assertEquals(dict(expected_out), dict(actual_out))

    def testRunNotebooks(self):
        input_glob = path.join('tests', 'input', '*.ipynb')
        for notebook_file in glob(input_glob):
            notebook_file_base = path.basename(notebook_file)
            print notebook_file_base
            expected_file = path.join('tests', 'expected', notebook_file_base)
            runner = NotebookRunner(notebook_file)
            runner.run_notebook(True)
            expected = read(open(expected_file), 'json')
            self.assert_notebooks_equal(expected, runner.nb)


if __name__ == '__main__':
    unittest.main()

