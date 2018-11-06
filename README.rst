KafkaLogHandler
===============

Provides a python ``logging`` compatible handler for producing messages to a
Kafka message bus.

Depends on the confluent_kafka module to connect to Kafka.

Designed to support both standard and structlog formats, and serializes log
data as JSON when published as a Kafka message.  Messages are normalized to be
more compatible with Logstash/Filebeat formats.

Usage
=====

**Example:**

::

  import logger

  from kafkaloghandler import KafkaLogHandler

  log = logging.getLogger()

  klh = KafkaLogHandler(bootstrap_servers=["test-kafka:9092"], topic="testtopic")

  log.addHandler(klh)

  data={'example':'structured data'}

  log.info('message to send to kafka', data=data)


**Parameters that can be provided to KafkaLogHandler:**

*bootstrap_servers*
  List of Kafka bootstrap servers to connect to.

  **default:** ``["localhost:9092"]``

*extra_config*
  Dictionary of extra `producer configuration
  <https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md>`_
  passed to librdkafka.

  NOTE: The ``bootstrap_servers`` parameter will overwrite
  ``bootstrap.servers``.

  **default:** ``{}``


*timeout*
  Timeout in seconds for flushing producer queue. See librdkafka docs.

  **default:** ``10.0``

*topic*
  String that sets the topic in Kafka.

  **default:** ``"kafkaloghandler"``

*key*
  String that sets the default key in Kafka, can be used for summarization within Kafka.

  NOTE: This default key can be overridden on a per-message basis by passing a
  dict to the logger with ``{"key": "new_key_for_this_message"}`` in it.

  **default:** ``"klh"``

*flatten*
  Flattens nested dictionaries and lists passed as structured logging into the parent
  dictionary layer, up to a certain depth.

  This is useful when logging to external systems that don't have good support
  for hierarchical data.

  Example dictionary: ``{'a': {'b': 'c'}}`` would be flattened to ``{'a.b': 'c'}``

  Example list: ``{'a': ['b', 'c']}`` would be flattened to ``{'a.0': 'b', 'a.1': 'c'}``

  If the depth is exceeded, any remaining deeper items will be added to the
  output under the flattened key.

  Set to ``0`` to turn off flattening.

  **default:** ``5``

*separator*
  Separator used between items when flattening.

  **default:** ``.``

*blacklist*
  List of top-level keys to discard from structured logs when outputting JSON.

  **default:** ``["_logger", "_name"]``


Testing
=======

Unit tests can be run with ``tox``
