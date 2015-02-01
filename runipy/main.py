
from __future__ import print_function

import argparse
from sys import stderr, stdout, stdin, exit
import os.path
import logging
import codecs
import runipy

from runipy.notebook_runner import NotebookRunner, NotebookError
from IPython.nbformat.current import read, write

from IPython.config import Config
from IPython.nbconvert.exporters.html import HTMLExporter

def main():
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    log_datefmt = '%m/%d/%Y %I:%M:%S %p'

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version', version=runipy.__version__,
            help='print version information')
    parser.add_argument('input_file', nargs='?',
            help='.ipynb file to run (or stdin)')
    parser.add_argument('output_file', nargs='?',
            help='.ipynb file to save cell output to')
    parser.add_argument('--quiet', '-q', action='store_true',
            help='don\'t print anything unless things go wrong')
    parser.add_argument('--overwrite', '-o', action='store_true',
            help='write notebook output back to original notebook')
    parser.add_argument('--html', nargs='?', default=False,
            help='output an HTML snapshot of the notebook')
    parser.add_argument('--template', nargs='?', default=False,
            help='template to use for HTML output')
    parser.add_argument('--pylab', action='store_true',
            help='start notebook with pylab enabled')
    parser.add_argument('--matplotlib', action='store_true',
            help='start notebook with matplotlib inlined')
    parser.add_argument('--skip-exceptions', '-s', action='store_true',
            help='if an exception occurs in a cell, continue running the subsequent cells')
    parser.add_argument('--stdout', action='store_true',
            help='print notebook to stdout (or use - as output_file')
    parser.add_argument('--stdin', action='store_true',
            help='read notebook from stdin (or use - as input_file)')
    parser.add_argument('--no-chdir', action='store_true',
            help="do not change directory to notebook's at kernel startup")
    parser.add_argument('--profile-dir',
            help="set the profile location directly")
    args = parser.parse_args()


    if args.overwrite:
        if args.output_file is not None:
            print('Error: output_filename must not be provided if '
                    '--overwrite (-o) given', file=stderr)
            exit(1)
        else:
            args.output_file = args.input_file

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt=log_datefmt)

    working_dir = None

    if args.input_file == '-' or args.stdin:  # force stdin
        payload = stdin
    elif not args.input_file and stdin.isatty():  # no force, empty stdin
        parser.print_help()
        exit()
    elif not args.input_file:  # no file -> default stdin
        payload = stdin
    else:  # must have specified normal input_file
        payload = open(args.input_file)
        working_dir = os.path.dirname(args.input_file)

    if args.no_chdir:
        working_dir = None

    if args.profile_dir:
        profile_dir = os.path.expanduser(args.profile_dir)
    else:
        profile_dir = None

    logging.info('Reading notebook %s', payload.name)
    nb = read(payload, 'json')
    nb_runner = NotebookRunner(nb, args.pylab, args.matplotlib, profile_dir, working_dir)

    exit_status = 0
    try:
        nb_runner.run_notebook(skip_exceptions=args.skip_exceptions)
    except NotebookError:
        exit_status = 1

    if args.output_file and args.output_file != '-':
        logging.info('Saving to %s', args.output_file)
        write(nb_runner.nb, open(args.output_file, 'w'), 'json')

    if args.stdout or args.output_file == '-':
        write(nb_runner.nb, stdout, 'json')
        print()

    if args.html is not False:
        if args.html is None:
            # if --html is given but no filename is provided,
            # come up with a sane output name based on the
            # input filename
            if args.input_file.endswith('.ipynb'):
                args.html = args.input_file[:-6] + '.html'
            else:
                args.html = args.input_file + '.html'

        if args.template is False:
            exporter = HTMLExporter()
        else:
            exporter = HTMLExporter(
                    config=Config({'HTMLExporter':{'template_file':args.template, 'template_path': ['.', '/']}}))

        logging.info('Saving HTML snapshot to %s' % args.html)
        output, resources = exporter.from_notebook_node(nb_runner.nb)
        codecs.open(args.html, 'w', encoding='utf-8').write(output)

    nb_runner.shutdown_kernel()

    if exit_status != 0:
        logging.warning('Exiting with nonzero exit status')
    exit(exit_status)


if __name__ == '__main__':
    main()

