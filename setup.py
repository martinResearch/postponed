try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

libname="postponed"
setup(
    name = libname,
    version="0.1",
    packages=['postponed'],
    ext_modules=[],
    include_dirs=[],
    install_requires=["typeguard"]
)

