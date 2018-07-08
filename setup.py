from setuptools import setup
import sys
if sys.version_info < (3,5):
    sys.exit("Python < 3.5 is not supported")

setup(
    name='MyPyR',
    version='0.0.2',
    description='Runtime-enforced type checking, casting, and overloads for Python 3',
    author='Matthew Long',
    # author_email='null@null.com',
    license='MIT',
    packages=['mypyr'],
    install_requires=['infix'],
    extras_require={
        'build': ["sphinx-autodoc-typehints","mypy","pyannotate"],
    }
)
