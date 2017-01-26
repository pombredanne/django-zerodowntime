#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='django-zerodowntime',
    version='0.3.0',
    description="A Django Migrations extension providing a framework for Zero Downtime Continuous Delivery.",
    long_description=readme + '\n\n' + history,
    author="Phil Plante",
    author_email='phil@rentlytics.com',
    url='https://github.com/rentlytics/django-zerodowntime',
    packages=[
        'zerodowntime'
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.8',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    test_suite='tests',
    tests_require=[
        'pytest==3.0.6',
        'pytest-django==3.1.2',
    ],
    license="MIT",
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
