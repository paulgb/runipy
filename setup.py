from setuptools import setup

import versioneer


using_ipy4 = False
try:
    from IPython import __version__ as ipyv
    from distutils.version import LooseVersion

    using_ipy4 = (ipyv >= LooseVersion("4"))
except ImportError:
    using_ipy4 = True

install_requires = [
    'Jinja2>=2.7.2',
    'Pygments>=1.6',
    'ipython>=2.3.1',
    'pyzmq>=14.1.0',
]
if using_ipy4:
    install_requires.extend([
        'ipykernel>=4.0.0',
        'nbconvert>=4.0.0',
        'nbformat>=4.0.0',
    ])

setup(name='runipy',
      version=versioneer.get_version(),
      description='Run IPython notebooks from the command line',
      url='https://github.com/paulgb/runipy',
      author='Paul Butler',
      author_email='paulgb@gmail.com',
      maintainer='John Kirkham',
      maintainer_email='jakirkham@gmail.com',
      classifiers=[
          'Framework :: IPython',
      ],
      install_requires=install_requires,
      packages=['runipy'],
      entry_points={
          'console_scripts': [
              'runipy = runipy.main:main'
          ]
      },
      cmdclass=versioneer.get_cmdclass(),
      test_suite="test_runipy"
)
