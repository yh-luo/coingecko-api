from setuptools import setup

from coingecko_api import __version__

setup(name='coingecko-api',
      version=__version__,
      packages=['coingecko_api'],
      license='MIT',
      description='',
      long_description='',
      long_description_content_type="text/markdown",
      author='',
      author_email='',
      install_requires=['requests', 'typing'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.7')
