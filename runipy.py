
import argparse
from Queue import Empty

from IPython.nbformat.current import read, write, NotebookNode
from IPython.kernel.blocking import BlockingKernelClient
from IPython.kernel import KernelManager

import platform
from time import sleep

def run_notebook(nb_in, nb_out):
    km = KernelManager()
    km.start_kernel()

    if platform.system() == 'Darwin':
        sleep(1)

    kc = km.client()
    kc.start_channels()

    shell = kc.shell_channel
    iopub = kc.iopub_channel

    nb = read(open(nb_in), 'json')
    for ws in nb.worksheets:
        for i, cell in enumerate(ws.cells):
            cell['outputs'] = list()

            if cell.cell_type != 'code':
                continue

            shell.execute(cell.input)
            reply = shell.get_msg(timeout=20)

            outs = list()
            while True:

                try:
                    msg = iopub.get_msg(timeout=1)
                    if msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                        break
                except Empty:
                    raise

                content =  msg['content']

                msg_type = msg['msg_type']
                if msg_type == 'status':
                    continue
                elif msg_type == 'pyin':
                    cell['prompt_number'] = content['execution_count']
                    continue
                elif msg_type == 'clear_output':
                    outs = list()
                    continue

                out = NotebookNode(output_type=msg_type)

                if msg_type == 'stream':
                    out.stream = content['name']
                    out.text = content['data']
                elif msg_type in ('display_data', 'pyout'):
                    for mime, data in content['data'].iteritems():
                        attr = mime.split('/')[-1].lower()
                        attr = attr.replace('+xml', '').replace('plain','text')
                        setattr(out, attr, data)
                    if msg_type == 'pyout':
                        out.prompt_number = content['execution_count']
                elif msg_type == 'pyerr':
                    out.ename = content['ename']
                    out.evalue = content['evalue']
                    out.traceback = content['traceback']
                else:
                    print 'unhandled iopub msg:', msg_type
                outs.append(out)

            cell['outputs'] = outs

    write(nb, open(nb_out, 'w'), 'json')
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    run_notebook(args.input_file, args.output_file)

if __name__ == '__main__':
    main()

