
from setuptools import setup, find_packages

setup(
    name='dream',
    version='0.0.1',
    license='LGPL',
    url='http://dream-simulation.eu/',
    packages=find_packages('.'),
    package_dir={'': '.', 'simulation': 'simulation'},
    install_requires=[
        'flask',
        'SimPy>=3',
        'xlrd',
        'xlwt',
        'pyparsing==1.5.7', # latest python2 compatible version
        'pydot',
        'numpy',
        'rpy2>=2.3,<2.4', # 2.4.1 does not work for me
        'zope.dottedname',
    ],
    entry_points=("""
    [console_scripts]
    dream_platform=dream.platform:main
    dream_simulation=dream.simulation.LineGenerationJSON:main
    manpy_cli=dream.simulation.ManPyCLI:main
    """),
    include_package_data=True,
    zip_safe=False,
    test_suite='dream.tests'
)
