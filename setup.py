from setuptools import find_packages, setup

setup(
      name='papeles',
      version='0.0.1',
      description='Python package for the analysis paper corpora.',
      long_description=open('README.rst').read(),
      url='https://github.com/glhuilli/papeles',
      author="Gaston L'Huillier",
      author_email='glhuilli@gmail.com',
      license='MIT License',
      packages=find_packages(),
      package_data={
            '': ['README.rst', 'LICENSE']
      },
      zip_safe=False,
      install_requires=[x.strip() for x in open("requirements.txt").readlines()])
