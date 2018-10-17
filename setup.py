#!/usr/bin/env python

# Copyright 2018-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read()


def parse_requirements(filename):
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='kafkaloghandler',
    version=version(),
    description='Kafka Logging Handler',
    long_description=readme(),
    classifiers=[
        'Topic :: System :: Logging',
        'Topic :: Internet :: Log Analysis',
        'License :: OSI Approved :: Apache Software License',
    ],
    keywords='kafka logging',
    url='https://gerrit.opencord.org/gitweb?p=kafkaloghandler.git',
    author='Zack Williams',
    author_email='zdw@opennetworking.org',
    packages=['kafkaloghandler'],
    license='Apache v2',
    install_requires=parse_requirements('requirements.txt'),
    include_package_data=True,
    zip_safe=False,
)
