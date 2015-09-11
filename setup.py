from setuptools import setup

import versioneer

import runipy

setup(name='runipy',
      version=versioneer.get_version(),
      description='Run IPython notebooks from the command line',
      url='https://github.com/paulgb/runipy',
      author='Paul Butler',
      author_email='paulgb@gmail.com',
      classifiers=[
          'Framework :: IPython',
      ],
      install_requires=[
          'Jinja2>=2.7.2',
          'Pygments>=1.6',
          'ipython>=2.3.1,<4',
          'pyzmq>=14.1.0',
      ],
      packages=['runipy'],
      entry_points={
          'console_scripts': [
              'runipy = runipy.main:main'
          ]
      },
      cmdclass=versioneer.get_cmdclass()
)
