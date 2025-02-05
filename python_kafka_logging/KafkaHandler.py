from kafka.client import SimpleClient
from kafka.producer import SimpleProducer, KeyedProducer
import logging


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, hosts_list, topic, **kwargs):
        logging.Handler.__init__(self)

        self.kafka_client = SimpleClient(hosts_list)
        self.key = kwargs.get("key", None)
        self.kafka_topic_name = topic

        if not self.key:
            self.producer = SimpleProducer(self.kafka_client, **kwargs)
        else:
            self.producer = KeyedProducer(self.kafka_client, **kwargs)

    def emit(self, record):
        # drop kafka logging to avoid infinite recursion
        if record.name == 'kafka':
            return
        try:
            # use default formatting
            msg = self.format(record)
            msg = msg.encode("utf-8")

            # produce message
            if not self.key:
                self.producer.send_messages(self.kafka_topic_name, msg)
            else:
                self.producer.send_messages(self.kafka_topic_name, self.key,
                                            msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        if self.producer is not None:
            self.producer.stop()
        logging.Handler.close(self)
