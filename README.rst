``runipy``: run IPython as a script
=====================================

The IPython notebook provides an interactive interface to a Python interpreter.

- **Literate programming**: the IPython notebook is an ideal format for
  writing "literate" programs, in which the code is part of a larger multi-media
  document. ``runipy`` lets you run such programs directly, without first
  converting to a pure Python script.
- **Report generation**: ``runipy`` can run the notebook and convert it into HTML
  in one go, making it an easy way to automate reports.
- **Data pipeline**: if you use IPython notebooks to create a data pipeline,
  ``runipy`` lets you automate that pipeline without losing the notebook
  formatting.

Requirements
------------

``runipy`` supports IPython versions 2.x and 3.x.

As of ``runipy`` 0.1.0, IPython version 1.x may not work.

Installation
------------

The easiest way to install ``runipy`` is with ``pip``::

    $ pip install runipy

Command-line use
----------------

To run a ``.ipynb`` file as a script, run::

    $ runipy MyNotebook.ipynb

To save the output of each cell back to the notebook file, run::

    $ runipy -o MyNotebook.ipynb

To save the notebook output as a *new* notebook, run::

    $ runipy MyNotebook.ipynb OutputNotebook.ipynb

To run a ``.ipynb`` file and genereate an ``HTML`` report, run::

    $ runipy MyNotebook.ipynb --html report.html

Passing Arguments
-----------------

You can pass arguments to the notebook through environment variables.
The use of environment variables is OS- and shell- dependent, but in a
typical UNIX-like environment they can be passed on the command line
before the program name::

    $ myvar=value runipy MyNotebook.ipynb

Then in the notebook, to access myvar::

    from os import environ
    myvar = environ['myvar']

``environ`` is just a ``dict``, so you can use ``.get()`` to fall back on
a default value::

    from os import environ
    myvar = environ.get('myvar', 'default!')

Stdin / Stdout
--------------

``runipy`` can read stdin and stdout and sit in a UNIX pipeline::

    $ runipy --stdout < MyNotebook.ipynb > OutputNotebook.ipynb

    $ cat MyNotebook.ipynb | runipy --stdout > OutputNotebook.ipynb


Programmatic use
----------------

It is also possible to run IPython notebooks from Python, using::

    from runipy.notebook_runner import NotebookRunner
    from IPython.nbformat.current import read

    notebook = read(open("MyNotebook.ipynb"), 'json')
    r = NotebookRunner(notebook)
    r.run_notebook()

and you can enable ``pylab`` with::

    r = NotebookRunner(notebook, pylab=True)
    
The notebook is stored in the object and can be saved using::

    from IPython.nbformat.current import write
    write(r.nb, open("MyOtherNotebook.ipynb", 'w'), 'json')

`run_notebook()` takes two optional arguments. The first, `skip_exceptions`, 
takes a boolean value (`False` by default). If `True`, exceptions will be ignored
and the notebook will continue to execute cells after encountering an exception.
The second argument is `progress_callback`, which must be either `None` or a
function that takes one argument. This function is called after execution of
each cell with the 0-based index of the cell just evaluated. This can be useful
for tracking progress of long-running notebooks.

Credit
------

Portions of the code are based on code by `Min RK <https://github.com/minrk>`_

Thanks to Kyle Kelley, Nitin Madnani, George Titsworth, Thomas Robitaille,
Andrey Tatarinov, Matthew Brett, Adam Haney, Nathan Goldbaum, Adam Ginsburg,
Gustavo Bragança, Tobias Brandt, Andrea Zonca, Aaron O'Leary, and
Simon Guillot for patches, documentation fixes, and suggestions.

