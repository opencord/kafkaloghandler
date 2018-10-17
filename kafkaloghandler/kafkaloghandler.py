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

# kafkaloghandler - logging handler that sends to Kafka

import json
import confluent_kafka
import logging
import sys


class KafkaLogHandler(logging.Handler):

    def __init__(self,
                 bootstrap_servers=["localhost:9092"],
                 key="klh",  # kafka default key
                 topic="kafkaloghandler",  # kafka default topic
                 timeout=10.0,  # kafka connection timeout
                 flatten=5,  # maximum depth of dict flattening
                 separator=".",  # separator used when flattening
                 blacklist=["_logger"],  # keys excluded from messages
                 ):

        logging.Handler.__init__(self)

        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.key = key
        self.flatten = flatten
        self.separator = separator
        self.blacklist = blacklist
        self.timeout = timeout
        self.producer = None

    def _connect(self):

        try:
            producer_config = {
                'bootstrap.servers': ','.join(self.bootstrap_servers),
            }

            self.producer = confluent_kafka.Producer(**producer_config)

        except confluent_kafka.KafkaError, e:
            print "Kafka Error: %s" % e
            # die if there's an error
            sys.exit(1)

    def _flatten(self, ns, toflatten, maxdepth):
        """ flatten dicts creating a key.subkey.subsubkey... hierarchy """

        # if max depth reached, return k:v dict
        if maxdepth < 1:
            return {ns: toflatten}

        flattened = {}

        for k, v in toflatten.iteritems():

            prefix = "%s%s%s" % (ns, self.separator, k)

            if isinstance(v, dict):
                flattened.update(self._flatten(prefix, v, maxdepth-1))
            else:
                flattened[prefix] = v

        return flattened

    def emit(self, record):

        recvars = {}

        message_key = self.key

        # fixup any structured arguments
        for k, v in vars(record).iteritems():
            # remove any items with keys in blacklist
            if k in self.blacklist:
                continue

            # if a "key" is found, use as the kafka key and remove
            if k is 'key':
                message_key = v
                continue

            # flatten any sub-dicts down, if enabled
            if self.flatten and isinstance(v, dict):
                recvars.update(self._flatten(k, v, self.flatten))
                continue

            recvars[k] = v

        # Replace unserializable items with repr version.
        # Otherwise, the log message may be discarded if it contains any
        # unserializable fields
        json_recvars = json.dumps(
            recvars,
            separators=(',', ':'),
            default=lambda o: repr(o),
            )

        if self.producer is None:
            self._connect()

        try:
            self.producer.produce(self.topic, json_recvars, message_key)

        except confluent_kafka.KafkaError, e:
            print "Kafka Error: %s" % e
            # currently don't do anything on failure...
            pass

    def flush(self):

        if self.producer:
            self.producer.flush(self.timeout)
