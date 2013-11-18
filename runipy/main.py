
import argparse
from sys import stderr
import logging
import codecs

from runipy.notebook_runner import NotebookRunner, NotebookError

from IPython.nbconvert.exporters.html import HTMLExporter

def main():
    log_format = '%(asctime)s %(message)s'
    log_datefmt = '%m/%d/%Y %I:%M:%S %p'

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
            help='.ipynb file to run')
    parser.add_argument('output_file', nargs='?',
            help='.ipynb file to save cell output to')
    parser.add_argument('--quiet', '-q', action='store_true',
            help='don\'t print anything unless things go wrong')
    parser.add_argument('--overwrite', '-o', action='store_true',
            help='write notebook output back to original notebook')
    parser.add_argument('--html', nargs='?', default=False,
            help='output an HTML snapshot of the notebook')
    parser.add_argument('--pylab', action='store_true',
            help='start notebook with pylab enabled')
    parser.add_argument('--skip-exceptions', '-s', action='store_true',
            help='if an exception occurs in a cell, continue running the subsequent cells')
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


    nb_runner = NotebookRunner(args.input_file, args.pylab)

    exit_status = 0
    try:
        nb_runner.run_notebook(skip_exceptions=args.skip_exceptions)
    except NotebookError:
        exit_status = 1

    if args.output_file:
        nb_runner.save_notebook(args.output_file)

    if args.html is not False:
        if args.html is None:
            # if --html is given but no filename is provided,
            # come up with a sane output name based on the
            # input filename
            if args.input_file.endswith('.ipynb'):
                args.html = args.input_file[:-6] + '.html'
            else:
                args.html = args.input_file + '.ipynb'

        logging.info('Saving HTML snapshot to %s' % args.html)
        exporter = HTMLExporter()
        output, resources = exporter.from_notebook_node(nb_runner.nb)
        codecs.open(args.html, 'w', encoding='utf-8').write(output)

    if exit_status != 0:
        logging.warning('Exiting with nonzero exit status')
    exit(exit_status)


if __name__ == '__main__':
    main()

