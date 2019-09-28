import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='structjour',
    version='0.9.91-Alpha.003',
    author='Mike Petersen',
    author_email='pentsok@zerosubstance.org',
    description='A structured daily journal for day traders.',
    license='GPL',
    long_description=long_description,
    url='https://github.com/MikePia/structjour',
    packages=setuptools.find_packages(exclude=['test']),
    keywords='DayTrading journal',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows'
    ],
    install_requires=[
        'numpy>=1.16.0',
        'pandas>=0.24.0',
        'seaborn>=0.9.0',
        'PyQtWebEngine>=5.12.1',
        'PyQt5>=5.13.0',
        'pyqt5-sip',
        'openpyxl>=2.5.14',
        'beautifulsoup4>=4.7.1',
        'mpl-finance==0.10.0'
    ],
    data_files=[('structjour/images', [
        'structjour/images/ZeroSubstanceCreation_220.png',
        'structjour/images/ZeroSubstanceCreation_500x334.png',
        'structjour/images/ZeroSubstanceCreation.png',
        'structjour/images/ZSLogo.png',
        'structjour/images/filesettings.png',
        'structjour/images/stockapi.png',
        'structjour/images/structjour.png'
    ]), ('', ['Disciplined.xlsx']),('',['readme.md'])],
    entry_points={'console_scripts': 'structjour=structjour.view.runtrade:main'},
    python_requires='>=3.6'
)
