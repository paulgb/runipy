
import argparse
from sys import stderr
import logging

from notebook_runner import NotebookRunner

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


    nb_runner = NotebookRunner(args.input_file)

    exit_status = 0
    try:
        nb_runner.run_notebook()
    except NotebookError:
        exit_status = 1

    if args.output_file:
        nb_runner.save_notebook(args.output_file)

    if exit_status != 0:
        logging.warning('Exiting with nonzero exit status')
    exit(exit_status)


if __name__ == '__main__':
    main()

