from distutils.core import setup

setup(
    name='JumpScale9',
    version='9.0.0',
    description='Automation framework for cloud workloads',
    url='https://github.com/Jumpscale/core9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=['JumpScale9'],
    install_requires=[
        'redis',
        'colorlog',
        'pytoml',
        'ipython',
        'colored_traceback',
        'pystache',
        'libtmux',
        'httplib2',
        'netaddr',
        'python-dateutil',
        'requests',
        'path.py',
        'click',
        'gitpython',
    ]
)
