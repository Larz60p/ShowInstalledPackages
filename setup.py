import os
from distutils.core import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='ShowInstalledPackages',
    packages=['ShowInstalledPackages'],  # this must be the same as the name above
    summary='List all user installed packages and details',
    version='0.1.1',
    author='Larry McCaig (Larz60+)',
    author_email='larry@dimplechad.com',
    long_description=read('README.md'),
    license="MIT",
    url='https://github.com/Larz60p/ShowInstalledPackages',
    download_url='https://github.com/Larz60p/ShowInstalledPackages/tarball/0.1.1',
    keywords='tools packages installed utilities',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Topic :: Utilities',
        'License :: MIT License',
    ],
)
