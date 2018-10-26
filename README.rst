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
  List of Kafka bootstrap servers to connect to. See confluent_kafka docs.

  **default:** ``["localhost:9092"]``

*timeout*
  Timeout in seconds for flushing producer queue. See confluent_kafka docs.

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
  Flattens nested dictionary keys passed as structured logging into the parent
  dictionary layer, up to a certain depth.

  This is useful when logging to external systems that don't have good support
  for hierarchical data.

  Example: ``{'a': {'b': 'c'}}`` would be flattened to ``{'a.b': 'c'}``

  If the depth is exceeded, any remaining deeper dict will be added to the
  output under the flattened key.

  Set to ``0`` to turn off flattening.

  **default:** ``5``

*separator*
  Separator used between keys when flattening.

  **default:** ``.``

*blacklist*
  List of top-level keys to discard from structured logs when outputting JSON.

  **default:** ``["_logger", "_name"]``


Tests
=====

Unit tests can be run with:

   nose2 --verbose --coverage-report term
