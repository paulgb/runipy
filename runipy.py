
import argparse
from Queue import Empty
import platform
from time import sleep
import logging
from sys import stderr


from IPython.nbformat.current import read, write, NotebookNode
from IPython.kernel import KernelManager

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

def run_notebook(nb_in, nb_out):
    exit_status = 0
    km = KernelManager()
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

    shell = kc.shell_channel
    iopub = kc.iopub_channel

    nb = read(open(nb_in), 'json')

    for ws in nb.worksheets:
        for i, cell in enumerate(ws.cells, 1):
            if cell.cell_type != 'code':
                continue

            logging.info('Running cell %s:\n%s\n', i, cell.input)
            shell.execute(cell.input)
            reply = shell.get_msg()

            outs = list()
            while True:

                try:
                    msg = iopub.get_msg(timeout=1)
                    if msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                        break
                except Empty:
                    # execution state should return to idle before the queue becomes empty,
                    # if it doesn't, something bad has happened
                    raise

                content =  msg['content']
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
                elif msg_type in ('display_data', 'pyout'):
                    for mime, data in content['data'].iteritems():
                        try:
                            attr = MIME_MAP[mime]
                        except KeyError:
                            print 'unknown mime type:', mime
                        
                        setattr(out, attr, data)
                elif msg_type == 'pyerr':
                    out.ename = content['ename']
                    out.evalue = content['evalue']
                    out.traceback = content['traceback']
                    logging.error('Exiting on error:\n%s', '\n'.join(content['traceback']))
                    exit_status = 1
                    break
                else:
                    print 'unhandled iopub msg:', msg_type
                outs.append(out)

            cell['outputs'] = outs

    if nb_out is not None:
        write(nb, open(nb_out, 'w'), 'json')
    exit(exit_status) 

def main():
    # TODO: options:
    # - output:
    #   - save HTML report (nbconvert)

    log_format = '%(asctime)s %(message)s'
    log_datefmt = '%m/%d/%Y %I:%M:%S %p'

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file', nargs='?')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--overwrite', '-o', action='store_true')
    args = parser.parse_args()


    if args.overwrite:
        if args.output_file is not None:
            print >> stderr, 'Error: output_filename must not be provided if '\
                    '--overwrite (-o) given'
            exit(1)
        else:
            args.output_file = args.input_file

    if not args.quiet:
        logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=log_datefmt)


    run_notebook(args.input_file, args.output_file)



if __name__ == '__main__':
    main()

