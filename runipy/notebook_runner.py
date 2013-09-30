
from __future__ import print_function

try:
    # python 2
    from Queue import Empty
except:
    # python 3
    from queue import Empty
import platform
from time import sleep
import logging

from IPython.nbformat.current import read, write, NotebookNode
from IPython.kernel import KernelManager


class NotebookError(Exception):
    pass


class NotebookRunner(object):
    # The kernel communicates with mime-types while the notebook
    # uses short labels for different cell types. We'll use this to
    # map from kernel types to notebook format types.

    MIME_MAP = {
        'image/jpeg': 'jpeg',
        'image/png': 'png',
        'text/plain': 'text',
        'text/html': 'html',
        'text/latex': 'latex',
    }

    def __init__(self, nb_in, pylab):
        km = KernelManager()
        if pylab:
            km.start_kernel(extra_arguments=['--pylab=inline'])
        else:
            km.start_kernel()

        if platform.system() == 'Darwin':
            # There is sometimes a race condition where the first
            # execute command hits the kernel before it's ready.
            # It appears to happen only on Darwin (Mac OS) and an
            # easy (but clumsy) way to mitigate it is to sleep
            # for a second.
            sleep(1)

        kc = km.client()
        kc.start_channels()

        self.shell = kc.shell_channel
        self.iopub = kc.iopub_channel

        logging.info('Reading notebook %s', nb_in)
        self.nb = read(open(nb_in), 'json')


    def run_cell(self, cell):
        '''
        Run a notebook cell and update the output of that cell in-place.
        '''
        logging.info('Running cell:\n%s\n', cell.input)
        self.shell.execute(cell.input)
        reply = self.shell.get_msg()
        status = reply['content']['status']
        if status == 'error':
            logging.info('Cell raised uncaught exception: %s', reply['content']['ename'])
        else:
            logging.info('Cell returned')

        outs = list()
        while True:
            try:
                msg = self.iopub.get_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty:
                # execution state should return to idle before the queue becomes empty,
                # if it doesn't, something bad has happened
                raise

            content = msg['content']
            msg_type = msg['msg_type']

            out = NotebookNode(output_type=msg_type)

            if 'execution_count' in content:
                cell['prompt_number'] = content['execution_count']
                out.prompt_number = content['execution_count']

            if msg_type in ['status', 'pyin']:
                continue
            elif msg_type == 'stream':
                out.stream = content['name']
                out.text = content['data']
                print(out.text, end='')
            elif msg_type in ('display_data', 'pyout'):
                for mime, data in content['data'].items():
                    try:
                        attr = self.MIME_MAP[mime]
                    except KeyError:
                        raise NotImplementedError('unhandled mime type: %s' % mime)
                    
                    setattr(out, attr, data)
                print(data, end='')
            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']

                logging.error('\n'.join(content['traceback']))
            else:
                raise NotImplementedError('unhandled iopub message: %s' % msg_type)
            outs.append(out)
        cell['outputs'] = outs

        if status == 'error':
            raise NotebookError()

    def iter_code_cells(self):
        '''
        Iterate over the notebook cells containing code.
        '''
        for ws in self.nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    yield cell


    def run_notebook(self):
        '''
        Run all the cells of a notebook in order and update
        the outputs in-place.
        '''
        for cell in self.iter_code_cells():
            self.run_cell(cell)

    
    def save_notebook(self, nb_out):
        logging.info('Saving to %s', nb_out)
        write(self.nb, open(nb_out, 'w'), 'json')

