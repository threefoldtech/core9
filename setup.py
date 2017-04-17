from distutils.core import setup

setup(name='jumpscale_core9',
      version='9.0.0',
      description='automation framework for cloud workloads',
      url='https://github.com/Jumpscale/core9',
      author='GIG',
      author_email='info@gig.tech',
      license='Apache',
      packages=['Jumpscale9'],
      install_requires=[
          'redis',
          'colorlog',
          'pytoml',
          'ipython',
          'colored_traceback',
          'pystache',
          'libtmux'
      ])
