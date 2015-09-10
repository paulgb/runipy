from __future__ import print_function

import unittest
from glob import glob
from os import path
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
            # don't match object's id; also happens to fix incompatible
            # results between IPython2 and IPython3 (which prints "object"
            # instead of "at [id]"
            cell['text'] = re.sub('at 0x[0-9a-f]+', 'object', cell['text'])
        if 'traceback' in cell:
            cell['traceback'] = [re.sub('\x1b\\[[01];\\d\\dm', '', line) for line in cell['traceback']]
            # rejoin lines, so it's one string to compare
            cell['traceback'] = u'\n'.join(cell['traceback'])
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
        notebook_dir = path.join('tests', 'input')
        for notebook_path in glob(path.join(notebook_dir, '*.ipynb')):
            notebook_file = path.basename(notebook_path)
            print(notebook_file)
            expected_file = path.join('tests', 'expected', notebook_file)
            notebook = ""
            with open(notebook_path) as notebook_file:
                notebook = read(notebook_file, 'json')
            runner = NotebookRunner(notebook, working_dir=notebook_dir)
            runner.run_notebook(True)
            expected = ""
            with open(expected_file) as notebook_file:
                expected = read(notebook_file, 'json')
            self.assert_notebooks_equal(expected, runner.nb)


if __name__ == '__main__':
    unittest.main()
