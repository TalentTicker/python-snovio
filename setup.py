from setuptools import setup

setup(
    name='python-snovio',
    version="0.1.5",
    license="MIT",

    install_requires=[
        "requests",
    ],

    description='A Python wrapper around Snov.io API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    url='https://github.com/TalentTicker/pip_stable',
    author='Talent Ticker',

    include_package_data=True,

    packages=['snovio'],

    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)