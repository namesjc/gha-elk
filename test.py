import datetime
import logging
from elasticsearch import Elasticsearch
import json

class ElasticsearchHandler(logging.Handler):
    def __init__(self, hosts, auth=None, index_prefix='gha-logs-'):
        super().__init__()
        self.es = Elasticsearch(hosts=hosts, basic_auth=auth)
        self.index_prefix = index_prefix

    def emit(self, record):
        log_entry = self.format(record)
        try:
            # mapping = {
            #     '@timestamp': self.format_timestamp(record.created),
            #     'level': record.levelname,
            #     'logger': record.name,
            #     'message': record.msg,
            #     'extra': record.extra
            # }
            # Add additional fields as needed
            index_name = f"{self.index_prefix}{datetime.datetime.now().strftime('%Y-%m-%d')}"
            if not self.es.indices.exists(index=index_name):
                self.es.index(index=index_name, body=json.loads(log_entry))
        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")

    @staticmethod
    def format_timestamp(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).isoformat()

# Example usage:
import logging

# Elasticsearch connection details
es_hosts = ['https://elastic.local.adiachan.cn:9200']
es_auth = ('elastic', 'changeme')  # Replace with your credentials

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# Create an Elasticsearch handler
es_handler = ElasticsearchHandler(hosts=es_hosts, auth=es_auth)
es_handler.setLevel(logging.INFO)

# Set up the formatter to log in JSON format
formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
es_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(es_handler)

# Log a message
logger.info('This is a log message')
