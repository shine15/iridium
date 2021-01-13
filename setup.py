import os
import platform
from setuptools import (
    find_packages,
    setup,
    Extension
)
from Cython.Build import cythonize
from numpy import get_include

ext_modules = [
    Extension('iridium.lib.trade',
              ['iridium/lib/trade.pyx'],
              include_dirs=['.', get_include()]
              ),
    Extension('iridium.lib.order',
              ['iridium/lib/order.pyx'],
              include_dirs=['.', get_include()]
              ),
    Extension('iridium.lib.forex',
              ['iridium/lib/forex.pyx'],
              extra_compile_args=['-fopenmp'],
              extra_link_args=['-fopenmp', '-Wl,-rpath,/usr/local/opt/gcc/lib/gcc/9/'],
              include_dirs=['.', get_include()]
              ),
    Extension('iridium.lib.instrument',
              ['iridium/lib/instrument.pyx']
              )
]

if platform.system() == 'Darwin':
    os.environ["CC"] = "gcc-9"
    os.environ["CXX"] = "gcc-9"

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
    ext_modules=cythonize(ext_modules),
    include_package_data=True,
    package_data={root.replace(os.sep, '.'): ['*.pyx', '*.pxd'] for root, dirnames, filenames in os.walk('iridium')
                  if '__pycache__' not in root},
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
        'click',
    ]
)
