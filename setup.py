from setuptools import setup

setup(name='arcticfox',
      version='0.1',
      description='Python package for communication with the ArcticFox firmware',
      url='https://github.com/Epictek/arcticfox-python',
      author='Kieran Coldron',
      author_email='kieran@coldron.com',
      license='GPL2',
      packages=['arcticfox'],
      install_requires=['pyusb']
)
