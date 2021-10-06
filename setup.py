from setuptools import setup

from coingecko_api import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='coingecko-api',
      version=__version__,
      packages=['coingecko_api'],
      license='MIT',
      description='Python wrapper around the CoinGecko API',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url = 'https://github.com/yh-luo/coingecko-api',
      author='Yu-Han Luo',
      author_email='yuhanluo1994@gmail.com',
      install_requires=['requests', 'typing'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.7')
