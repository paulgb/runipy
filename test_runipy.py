from __future__ import print_function

import unittest
from glob import glob
from os import devnull, path
import re
import sys
import warnings

with warnings.catch_warnings():
    try:
        from IPython.utils.shimmodule import ShimWarning
        warnings.filterwarnings('error', '', ShimWarning)
    except ImportError:
        class ShimWarning(Warning):
            """Warning issued by iPython 4.x regarding deprecated API."""
            pass

    try:
        # IPython 3
        from IPython.nbformat import reads, NBFormatError
    except ShimWarning:
        # IPython 4
        from nbformat import reads, NBFormatError
    except ImportError:
        # IPython 2
        from IPython.nbformat.current import reads, NBFormatError
    finally:
        warnings.resetwarnings()

from runipy.main import main
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
            trsub = lambda l: re.sub('\x1b\\[[01];\\d\\dm', '', l)
            cell['traceback'] = [trsub(line) for line in cell['traceback']]
            # rejoin lines, so it's one string to compare
            cell['traceback'] = u'\n'.join(cell['traceback'])
            # Python 3 describes a ZeroDivisionError differently.
            # We change the Python 2 wording to the Python 3 wording.
            cell['evalue'] = re.sub(
                'integer division or modulo by zero',
                'division by zero',
                cell['evalue']
            )
            cell['traceback'] = re.sub(
                'integer division or modulo by zero',
                'division by zero',
                cell['traceback']
            )
        return cell

    def assert_notebooks_equal(self, expected, actual):
        self.assertEqual(
            len(expected['worksheets'][0]['cells']),
            len(actual['worksheets'][0]['cells'])
        )

        for expected_out, actual_out in zip(
                expected['worksheets'][0]['cells'],
                actual['worksheets'][0]['cells']
        ):
            for k in set(expected_out).union(actual_out):
                if k == 'outputs':
                    self.assertEqual(len(expected_out[k]), len(actual_out[k]))
                    for e, a in zip(expected_out[k], actual_out[k]):
                        e = self.prepare_cell(e)
                        a = self.prepare_cell(a)
                        self.assertEqual(a, e)

    def testRunNotebooks(self):
        notebook_dir = path.join('tests', 'input')
        for notebook_path in glob(path.join(notebook_dir, '*.ipynb')):
            notebook_file = path.basename(notebook_path)
            print(notebook_file)
            expected_file = path.join('tests', 'expected', notebook_file)
            notebook = ""
            with open(notebook_path) as notebook_file:
                notebook = notebook_file.read()
            try:
                # IPython 3
                notebook = reads(notebook, 3)
            except (TypeError, NBFormatError):
                # IPython 2
                notebook = reads(notebook, 'json')
            runner = NotebookRunner(notebook, working_dir=notebook_dir)
            runner.run_notebook(True)
            expected = ""
            with open(expected_file) as notebook_file:
                expected = notebook_file.read()
            try:
                # IPython 3
                expected = reads(expected, 3)
            except (TypeError, NBFormatError):
                # IPython 2
                expected = reads(expected, 'json')
            self.assert_notebooks_equal(expected, runner.nb)

    def testUseCLI(self):
        notebook_dir = path.join('tests', 'expected')
        for notebook_path in glob(path.join(notebook_dir, '*.ipynb')):
            notebook_file = path.basename(notebook_path)
            print(notebook_file)
            expected = ""
            with open(notebook_path) as notebook_file:
                expected = notebook_file.read()
            try:
                # IPython 3
                expected = reads(expected, 3)
            except (TypeError, NBFormatError):
                # IPython 2
                expected = reads(expected, 'json')
            exit_code = 1
            argv = sys.argv
            stdout = sys.stdout
            stderr = sys.stderr
            try:
                with open(devnull, "w") as devnull_filehandle:
                    sys.stdout = sys.stderr = devnull_filehandle
                    sys.argv = [
                        "runipy",
                        "-o", notebook_path,
                        "--html", notebook_path.replace(".ipynb", ".html")
                    ]
                    main()
            except SystemExit as e:
                exit_code = e.code
            finally:
                sys.argv = argv
                sys.stdout = stdout
                sys.stderr = stderr
            notebook = ""
            with open(notebook_path) as notebook_file:
                notebook = notebook_file.read()
            try:
                # IPython 3
                notebook = reads(notebook, 3)
            except (TypeError, NBFormatError):
                # IPython 2
                notebook = reads(notebook, 'json')
            self.assert_notebooks_equal(expected, notebook)


if __name__ == '__main__':
    unittest.main()
