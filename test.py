
import unittest
from glob import glob
from os import path, chdir
import re

from IPython.nbformat.current import read

from runipy.notebook_runner import NotebookRunner

class TestRunipy(unittest.TestCase):
    maxDiff = 100000

    def prepare_cell(self, cell):
        cell = dict(cell)
        if 'metadata' in cell:
            del cell['metadata']
        if 'text' in cell:
            cell['text'] = re.sub('0x[0-9a-f]{7,9}', '<HEXADDR>', cell['text'])
        return cell


    def assert_notebooks_equal(self, expected, actual):
        self.assertEquals(len(expected['worksheets'][0]['cells']),
                len(actual['worksheets'][0]['cells']))

        for expected_out, actual_out in zip(expected['worksheets'][0]['cells'],
                actual['worksheets'][0]['cells']):
            for k in set(expected_out).union(actual_out):
                if k == 'outputs':
                    self.assertEquals(len(expected_out[k]), len(actual_out[k]))
                    for e, a in zip(expected_out[k], actual_out[k]):
                        e = self.prepare_cell(e)
                        a = self.prepare_cell(a)
                        self.assertEquals(a, e)
                    

    def testRunNotebooks(self):
        chdir(path.join('tests', 'input'))
        for notebook_file in glob('*.ipynb'):
            print notebook_file
            expected_file = path.join('..', 'expected', notebook_file)
            runner = NotebookRunner(read(open(notebook_file), 'json'))
            runner.run_notebook(True)
            expected = read(open(expected_file), 'json')
            self.assert_notebooks_equal(expected, runner.nb)


if __name__ == '__main__':
    unittest.main()

