
from setuptools import setup, find_packages

import finddata

package_data = {
    'dream.platform': finddata.find_package_data()['dream.platform']
}

setup(
    name='dream',
    version='0.0.1',
    license='LGPL',
    packages=find_packages('.'),
    package_dir={'': '.', 'simulation': 'simulation'},
    package_data=package_data,
    install_requires=[
        'flask',
        'SimPy>=2,<3',
        'xlrd',
        'xlwt',
        'pyparsing==1.5.7',
        'pydot',
        'numpy',
        'rpy2',
    ],
    entry_points=("""
    [console_scripts]
    dream_platform=dream.platform:main
    dream_simulation=dream.simulation.LineGenerationJSON:main
    dream_run=dream.platform:run
    """),
    include_package_data=True,
    zip_safe=False,
    test_suite='dream.tests'
)
