import setuptools



thePackages = setuptools.find_packages(exclude=['test'])
thePackages.append('structjour.images')

print(thePackages)