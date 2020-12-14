from setuptools import setup
import sys
if sys.version_info < (3,5):
    sys.exit("Python < 3.5 is not supported")

setup(
    name='MyDiPy',
    version='0.0.1',
    description='Function overloading, type checking, multiple dispatch, inheritance, and casting in Python 3.5+',
    long_description='Runtime-enforced type checking, method/function overloading, multiple dispatch, inheritance, and casting for Python 3.5+. Uses MyPy/PEP 484-style annotations but where it actually is enforced at runtime.',
    author='Matthew Long',
    url='https://github.com/long-m-r/MyDiPy',
    # author_email='null@null.com',
    license='MIT',
    packages=['mydipy'],
    install_requires=['infix']
)
