import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='structjour',
    version='0.9.9-Alpha',
    author='Mike Petersen',
    author_email='pentsok@zerosubstance.org',
    description='A structured daily journal for day traders.',
    license='GPL',
    long_description=long_description,
    url='https://github.com/MikePia/structjour',
    packages=setuptools.find_packages(exclude=['test']),
    keywords='DayTrading journal',
    classifiers=[
        'Development Status :: - Alpha',
        'Intended Audience :: Day Traders'
        'Programming Language :: Python :: 3',
        'License :: GNU GPL Version 3',
        'Operating System :: Windows',
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
    data_files=[('images', [
        'images/ZeroSubstanceCreation_220.png',
        'images/ZeroSubstanceCreation_500x334.png',
        'images/ZeroSubstanceCreation.png',
        'images/ZSLogo.png',
        'images/filesettings.png',
        'images/stockapi.png',
        'images/structjour.png'
    ]), ('', ['Disciplined.xlsx'])],
    entry_points={'console_scripts': 'structjour=structjour.view.runtrade:main'},
    python_requires='>=3.6'
)
