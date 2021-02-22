import setuptools
from shutil import copyfile
# import os

copyfile('readme.md', 'structjour/readme.md')


with open('structjour/readme.md', 'r') as fh:
    long_description = fh.read()


thePackages = setuptools.find_packages(exclude=['test'])

setuptools.setup(
    name='structjour',
    version='0.9.95-Alpha.001',
    author='Mike Petersen',
    author_email='pentsok@zerosubstance.org',
    description='A structured daily journal for day traders.',
    license='GPL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MikePia/structjour',
    packages=thePackages,
    keywords='DayTrading journal',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows'
    ],
    install_requires=[
        'requests',
        'Pillow',
        'numpy>=1.16.0',
        'pandas>=0.24.0',
        'matplotlib>=3.1.0',
        'sqlalchemy>=1.3.16',
        'seaborn>=0.9.0',
        'PyQtWebEngine>=5.12.1',
        'PyQt5>=5.13.0',
        'pyqt5-sip',
        'openpyxl>=2.5.14',
        'beautifulsoup4>=4.7.1',
        'mpl-finance==0.10.0'
    ],
    include_package_data=True,

    # data_files=[('', ['Disciplined.xlsx']),('',['readme.md'])],
    entry_points={'console_scripts': 'structjour=structjour.view.runtrade:main'},
    python_requires='>=3.6'
)
