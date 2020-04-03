from setuptools import setup, find_packages

setup(
    name='dream',
    version='0.0.1',
    license='LGPL',
    url='https://manpy-simulation.org/',
    packages=find_packages('.'),
    package_dir={'': '.', 'simulation': 'simulation'},
    install_requires=[
        'flask',
        'SimPy>=3',
        'xlrd',
        'xlwt',
        'pyparsing',
        'pydot',
        'numpy',
        'zope.dottedname',
        'rpy2',
        'pulp',
        'tablib',
        'mysqlclient',
    ],
    entry_points=("""
    [console_scripts]
    dream_platform=dream.platform:main
    dream_simulation=dream.simulation.LineGenerationJSON:main
    """),
    include_package_data=True,
    zip_safe=False,
    test_suite='dream.tests'
)
