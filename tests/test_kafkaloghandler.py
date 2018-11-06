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

from kafkaloghandler import KafkaLogHandler
import json
import logging
import unittest

# mock is a part of unittest in python 3
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


class FakeKafkaProducer():
    '''
    Works like Producer in confluent_kafka, ref:
    https://docs.confluent.io/current/clients/confluent-kafka-python/#producer
    '''
    def __init__(self, config=[]):
        self.config = config

    def produce(self, topic, value='', key=''):
        self.topic = topic
        self.value = value
        self.key = key

    def poll(self, timeout=1):
        self.poll_timeout = timeout

    def flush(self, timeout=1):
        self.flush_timeout = timeout


class TestKafkaLogHandler(unittest.TestCase):

    def setUp(self):
        '''
        Setup tests for KafkaLogHandler, mainly common init of logger
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.handlers = []
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        logging.shutdown()

    def test_single_message(self):
        '''
        tests that _emit is called once when there is one message
        '''

        with patch.object(KafkaLogHandler, 'emit') as emit:

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic")

            self.logger.addHandler(klh)

            self.logger.warn('Warning')

            assert emit.call_count == 1

    def test_config(self):
        '''
        tests that producer_config dictionary is built correctly
        '''

        ec = {"queue.buffering.max.messages": 1000,
              "queue.buffering.max.kbytes": 512,
              "bootstrap.servers": 'foo'}

        klh = KafkaLogHandler(
                bootstrap_servers=["tk1:9092", "tk2:9093"],
                extra_config=ec,
                topic="testtopic")

        self.assertEqual(klh.producer_config,
                         {"bootstrap.servers": "tk1:9092,tk2:9093",
                          "queue.buffering.max.messages": 1000,
                          "queue.buffering.max.kbytes": 512})

    def test_with_structure(self):
        '''
        tests structured serialization of log to JSON
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic")

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "bar": "value2",
                "l1": {"l2": {'l3': "nested"}},
            }

            self.logger.info('structured', extra=extra_data)

            decoded_message = json.loads(klh.producer.value)

            self.assertEqual(klh.producer.topic, 'testtopic')
            self.assertEqual(decoded_message['message'], 'structured')
            self.assertEqual(decoded_message['foo'], 'value1')
            self.assertEqual(decoded_message['bar'], 'value2')
            self.assertEqual(decoded_message['l1.l2.l3'], 'nested')

    def test_without_flatten(self):
        '''
        tests with flattening of objects disabled
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic",
                                  flatten=0)

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "l1": {"l2": {'l3': "nested"}},
            }

            self.logger.info('noflatten', extra=extra_data)

            decoded_message = json.loads(klh.producer.value)

            self.assertEqual(decoded_message['message'], 'noflatten')
            self.assertEqual(decoded_message['foo'], 'value1')
            self.assertEqual(decoded_message['l1'], {'l2': {'l3': "nested"}})

    def test_with_shallow_flatten(self):
        '''
        Tests with a shallow flattening of objects, and different separator
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic",
                                  flatten=1,
                                  separator='_')

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "l1": {"l2": {'l3': "nested"}},
            }

            self.logger.info('oneflatten', extra=extra_data)

            decoded_message = json.loads(klh.producer.value)

            self.assertEqual(decoded_message['message'], 'oneflatten')
            self.assertEqual(decoded_message['foo'], 'value1')
            self.assertEqual(decoded_message['l1_l2'], {'l3': 'nested'})

    def test_flatten_list(self):
        '''
        Tests flattening of lists
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic")

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "list": ['item0', 'item1', {'dict': 'in_list'}],
            }

            self.logger.info('listflatten', extra=extra_data)

            decoded_message = json.loads(klh.producer.value)

            self.assertEqual(decoded_message['message'], 'listflatten')
            self.assertEqual(decoded_message['foo'], 'value1')
            self.assertEqual(decoded_message['list.0'], 'item0')
            self.assertEqual(decoded_message['list.1'], 'item1')
            self.assertEqual(decoded_message['list.2.dict'], 'in_list')

    def test_override_key(self):
        '''
        Test setting the key argument to override the default
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic")

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "l1": {"l2": {'l3': "nested"}},
            }

            # log with default 'klh' key
            self.logger.info('defaultkey', extra=extra_data)

            decoded_message1 = json.loads(klh.producer.value)

            self.assertEqual(klh.producer.key, 'klh')
            self.assertEqual(decoded_message1['foo'], 'value1')
            self.assertEqual(decoded_message1['message'], 'defaultkey')
            self.assertEqual(decoded_message1['l1.l2.l3'], 'nested')

            # log with key overridden
            extra_data.update({'key': 'override'})
            self.logger.info('keyoverride', extra=extra_data)

            decoded_message2 = json.loads(klh.producer.value)

            self.assertEqual(klh.producer.key, 'override')
            self.assertEqual(decoded_message2['message'], 'keyoverride')
            self.assertEqual(decoded_message2['foo'], 'value1')
            self.assertEqual(decoded_message2['l1.l2.l3'], 'nested')

    def test_blacklist(self):
        '''
        tests adding items to blacklist
        '''

        with patch.object(KafkaLogHandler, '_connect'):

            klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"],
                                  topic="testtopic",
                                  blacklist=["bar"])

            klh.producer = FakeKafkaProducer()

            self.logger.addHandler(klh)

            extra_data = {
                "foo": "value1",
                "bar": "value2",
                "l1": {"l2": {'l3': "nested"}},
            }

            self.logger.info('blacklist', extra=extra_data)

            decoded_message = json.loads(klh.producer.value)

            self.assertEqual(klh.producer.topic, 'testtopic')
            self.assertEqual(decoded_message['message'], 'blacklist')
            self.assertEqual(decoded_message['foo'], 'value1')
            with self.assertRaises(KeyError):
                decoded_message['bar']
