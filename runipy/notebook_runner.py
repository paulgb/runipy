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
import os

from IPython.nbformat.current import NotebookNode
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
        'application/javascript': 'html',
        'image/svg+xml': 'svg',
    }


    def __init__(self, nb, pylab=False, mpl_inline=False, profile_dir=None, working_dir=None):
        self.km = KernelManager()

        args = []

        if pylab:
            args.append('--pylab=inline')
            logging.warn('--pylab is deprecated and will be removed in a future version')
        elif mpl_inline:
            args.append('--matplotlib=inline')
            logging.warn('--matplotlib is deprecated and will be removed in a future version')

        if profile_dir:
            args.append('--profile-dir=%s' % os.path.abspath(profile_dir))

        cwd = os.getcwd()

        if working_dir:
            os.chdir(working_dir)

        self.km.start_kernel(extra_arguments = args)
        
        os.chdir(cwd)

        if platform.system() == 'Darwin':
            # There is sometimes a race condition where the first
            # execute command hits the kernel before it's ready.
            # It appears to happen only on Darwin (Mac OS) and an
            # easy (but clumsy) way to mitigate it is to sleep
            # for a second.
            sleep(1)

        self.kc = self.km.client()
        self.kc.start_channels()
        try:
            self.kc.wait_for_ready()
        except AttributeError:
            # IPython < 3
            self._wait_for_ready_backport()

        self.nb = nb
        

    def shutdown_kernel(self):
        logging.info('Shutdown kernel')
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)
    
    def _wait_for_ready_backport(self):
        """Backport BlockingKernelClient.wait_for_ready from IPython 3"""
        # Wait for kernel info reply on shell channel
        self.kc.kernel_info()
        while True:
            msg = self.kc.get_shell_msg(block=True, timeout=30)
            if msg['msg_type'] == 'kernel_info_reply':
                break

        # Flush IOPub channel
        while True:
            try:
                msg = self.kc.get_iopub_msg(block=True, timeout=0.2)
            except Empty:
                break

    def run_cell(self, cell):
        '''
        Run a notebook cell and update the output of that cell in-place.
        '''
        logging.info('Running cell:\n%s\n', cell.input)
        self.kc.execute(cell.input)
        reply = self.kc.get_shell_msg()
        status = reply['content']['status']
        if status == 'error':
            traceback_text = 'Cell raised uncaught exception: \n' + \
                '\n'.join(reply['content']['traceback'])
            logging.info(traceback_text)
        else:
            logging.info('Cell returned')

        outs = list()
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty:
                # execution state should return to idle before the queue becomes empty,
                # if it doesn't, something bad has happened
                raise

            content = msg['content']
            msg_type = msg['msg_type']

            # IPython 3.0.0-dev writes pyerr/pyout in the notebook format but uses
            # error/execute_result in the message spec. This does the translation
            # needed for tests to pass with IPython 3.0.0-dev
            notebook3_format_conversions = {
                'error': 'pyerr',
                'execute_result': 'pyout'
            }
            msg_type = notebook3_format_conversions.get(msg_type, msg_type)

            out = NotebookNode(output_type=msg_type)

            if 'execution_count' in content:
                cell['prompt_number'] = content['execution_count']
                out.prompt_number = content['execution_count']

            if msg_type in ('status', 'pyin', 'execute_input'):
                continue
            elif msg_type == 'stream':
                out.stream = content['name']
                # in msgspec 5, this is name, text
                # in msgspec 4, this is name, data
                if 'text' in content:
                    out.text = content['text']
                else:
                    out.text = content['data']
                #print(out.text, end='')
            elif msg_type in ('display_data', 'pyout'):
                for mime, data in content['data'].items():
                    try:
                        attr = self.MIME_MAP[mime]
                    except KeyError:
                        raise NotImplementedError('unhandled mime type: %s' % mime)

                    setattr(out, attr, data)
                #print(data, end='')
            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']

                #logging.error('\n'.join(content['traceback']))
            elif msg_type == 'clear_output':
                outs = list()
                continue
            else:
                raise NotImplementedError('unhandled iopub message: %s' % msg_type)
            outs.append(out)
        cell['outputs'] = outs

        if status == 'error':
            raise NotebookError(traceback_text)


    def iter_code_cells(self):
        '''
        Iterate over the notebook cells containing code.
        '''
        for ws in self.nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    yield cell


    def run_notebook(self, skip_exceptions=False, progress_callback=None):
        '''
        Run all the cells of a notebook in order and update
        the outputs in-place.

        If ``skip_exceptions`` is set, then if exceptions occur in a cell, the
        subsequent cells are run (by default, the notebook execution stops).
        '''
        for i, cell in enumerate(self.iter_code_cells()):
            try:
                self.run_cell(cell)
            except NotebookError:
                if not skip_exceptions:
                    raise
            if progress_callback:
                progress_callback(i)


    def count_code_cells(self):
        '''
        Return the number of code cells in the notebook
        '''
        return sum(1 for _ in self.iter_code_cells())
        
