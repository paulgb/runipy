from distutils.version import LooseVersion
from setuptools import setup

import versioneer


using_ipy4 = False
try:
    from IPython import __version__ as ipyv
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

readme = ""
with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(
    name='runipy',
    version=versioneer.get_version(),
    license="BSD 2-Clause",
    description='Run IPython notebooks from the command line',
    long_description=readme,
    url='https://github.com/paulgb/runipy',
    author='Paul Butler',
    author_email='paulgb@gmail.com',
    maintainer='John Kirkham',
    maintainer_email='jakirkham@gmail.com',
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Framework :: IPython',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ipython',
    install_requires=install_requires,
    packages=['runipy'],
    entry_points={
        'console_scripts': [
            'runipy = runipy.main:main'
        ]
    },
    cmdclass=versioneer.get_cmdclass(),
    test_suite="test_runipy",
    zip_safe=True
)
