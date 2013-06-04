
from setuptools import setup, find_packages

setup(
    name='dream',
    version='0.0.1',
    license='LGPL',
    packages=find_packages('.'),
    package_dir={'': '.', 'simulation': 'simulation'},
    install_requires=[
        'flask',
        'Simpy',
        'xlrd',
        'xlwt',
    ],
    entry_points=("""
    [console_scripts]
    dream_platform=dream.platform:main
    dream_simulation=simulation.LineGenerationJSON:main
    """),
    include_package_data=True,
    zip_safe=False,
)
