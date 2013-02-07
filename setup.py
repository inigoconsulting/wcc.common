from setuptools import setup, find_packages
import os

version = '1.3.dev0'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='wcc.common',
      version=version,
      description="Common code among all WCC sites",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone wcc',
      author='Inigo Consulting',
      author_email='team@inigo-tech.com',
      url='https://github.com/inigoconsulting/wcc.common',
      license='gpl',
      packages=find_packages(),
      namespace_packages=['wcc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.interfaces'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      """,
      )
