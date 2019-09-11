import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='structjour',
    version='0.9.1-Alpha+000',
    author='Mike Petersen',
    author_email='pentsok@zerosubstance.org',
    description='A structured daily journal for day traders.',
    license='GPL',
    long_description=long_description,
    url='https://github.com/MikePia/structjour',
    packages=setuptools.find_packages(exclude=['tests']),
    keywords='DayTrading journal',
    classifiers=[
        'Development Status :: - Alpha',
        'Intended Audience :: Day Traders'
        'Programming Language :: Python :: 3',
        'License :: GNU GPL Version 3',
        'Operating System :: Windows',
    ],
    install_requires=[
        'PyQt5>=5.13.0',
        'PyQtWebEngine>=5.12.1',
        'openpyxl==2.5.14',
        'beautifulsoup4>=4.7.1',
        'mpl-finance==0.10.0'
    ],
    data_files=[('images', [
        'images/ZeroSubstanceCreation_220.png',
        'images/ZeroSubstanceCreation_500x334.png',
        'images/ZeroSubstanceCreation.png',
        'images/ZSLogo.png'
    ])],
    entry_points={'console_scripts': 'structjour=structjour.view.runtrade:main'},
    python_requires='>=3.6'
)


# figure out:
# entry_points
# package_data
# data_files
# extras_require
# and how to include IBAPI  optional