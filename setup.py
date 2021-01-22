import os
import platform
from setuptools import (
    find_packages,
    setup
)

setup(
    name='iridium',
    url="https://iridium77.org",
    version='0.1',
    description='Forex automation trading',
    entry_points={
        'console_scripts': [
            'iridium = iridium.__main__:cli',
        ],
    },
    author='Yu Su',
    author_email='super.iridium77@gmail.com',
    packages=find_packages(include=['iridium', 'iridium.*']),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Intended Audience :: Forex Trading',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing',
    ],
    install_requires=[
        'click', 'pandas', 'numpy', 'matplotlib'
    ]
)
