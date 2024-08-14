# builtins
import logging
import os
import json
import datetime
import sys
import threading
# third party
import elasticsearch
from elasticsearch.helpers import bulk

ELASTIC_HOST = os.environ.get("INPUT_ELASTIC_HOST", "https://elastic.local.adiachan.cn:9200")
ELASTIC_API_KEY_ID = os.environ.get("INPUT_ELASTIC_API_KEY_ID", "hycxUZEBX3AkgTy1jlk7")
ELASTIC_API_KEY = os.environ.get("INPUT_ELASTIC_API_KEY", "obxALXV-SaaJINiM5KpuJA")
ELASTIC_INDEX = os.environ.get("INPUT_ELASTIC_INDEX", "gha-logs")

try:
    assert ELASTIC_HOST not in (None, '')
except:
    output = "The input ELASTIC_HOST is not set"
    print(f"Error: {output}")
    sys.exit(-1)

try:
    assert ELASTIC_API_KEY_ID not in (None, '')
except:
    output = "The input ELASTIC_API_KEY_ID is not set"
    print(f"Error: {output}")
    sys.exit(-1)

try:
    assert ELASTIC_API_KEY not in (None, '')
except:
    output = "The input ELASTIC_API_KEY is not set"
    print(f"Error: {output}")
    sys.exit(-1)

try:
    assert ELASTIC_INDEX not in (None, '')
    now = datetime.datetime.now()
    elastic_index = f"{ELASTIC_INDEX}-{now.month}-{now.day}"
except:
    output = "The input ELASTIC_INDEX is not set"
    print(f"Error: {output}")
    sys.exit(-1)

class ElasticHandler(logging.Handler):

    def __init__(self, hosts, auth=None, index_prefix='gha-logs-'):
        super().__init__()
        self.es = elasticsearch.Elasticsearch(hosts=hosts, basic_auth=auth)
        self.index_prefix = index_prefix

    def emit(self, record):
        mapping = {
                '@timestamp': self.format_timestamp(record.created),
                'level': record.levelname,
                'logger': record.name,
                'message': record.msg,
                'severity': record.levelname,
                'thread_id': threading.get_ident(),
                'module': record.module,
                'function': record.funcName,
                'process': record.process,
                'processName': record.processName,
                'logger_name': record.name,
            }
        try:
            index_name = f"{self.index_prefix}{datetime.datetime.now().strftime('%Y-%m-%d')}"
            if not self.es.indices.exists(index=index_name):
                self.es.index(index=index_name, body=mapping)
        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")

    @staticmethod
    def format_timestamp(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).isoformat()
