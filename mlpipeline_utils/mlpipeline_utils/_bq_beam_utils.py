import logging
import os

import apache_beam as beam
from google.cloud import bigquery
import tensorflow as tf


__all__ = [
    'BigQueryToTFExampleConverter',
    'WriteBigQueryRowsToTFRecord',
]


class BigQueryToTFExampleConverter:

    def __init__(self, query):
        client = bigquery.Client()
        query_job = client.query('SELECT * FROM ({}) LIMIT 0'.format(query))
        results = query_job.result()
        self._type_map = {}
        for field in results.schema:
            self._type_map[field.name] = field.field_type

    def __call__(self, instance):
        feature = {}
        for key, value in instance.items():
            data_type = self._type_map[key]
            if value is None:
                feature[key] = tf.train.Feature()
            else:
                repeated_value = value if isinstance(value, list) else [value]
                if data_type == 'INTEGER':
                    feature[key] = tf.train.Feature(
                        int64_list=tf.train.Int64List(value=repeated_value)
                    )
                elif data_type == 'FLOAT':
                    feature[key] = tf.train.Feature(
                        float_list=tf.train.FloatList(value=repeated_value)
                    )
                elif data_type == 'STRING':
                    feature[key] = tf.train.Feature(
                        bytes_list=tf.train.BytesList(
                            value=[tf.compat.as_bytes(s) for s in repeated_value]
                        )
                    )
                else:
                    raise RuntimeError(
                        'BigQuery column type {} is not supported.'.format(data_type)
                    )
        return tf.train.Example(features=tf.train.Features(feature=feature))


class WriteBigQueryRowsToTFRecord(beam.PTransform):

    def __init__(self,
                 converter,
                 output_dir,
                 columns_to_discard=None):
        self._converter = converter
        self._output_dir = output_dir
        self._columns_to_discard = columns_to_discard or []

    def expand(self, pcoll):

        def discard_column_fn(row):
            for c in self._columns_to_discard:
                del row[c]
            return row

        return (
            pcoll
            | 'DiscardColumns' >> beam.Map(discard_column_fn)
            | 'BigQueryRowToTFExample' >> beam.Map(self._converter)
            | 'SerializeDeterministically' >> beam.Map(lambda x: x.SerializeToString(deterministic=True))
            | 'Shuffle' >> beam.transforms.Reshuffle()
            | 'WriteToTFRecord' >> beam.io.WriteToTFRecord(os.path.join(self._output_dir, 'part'), file_name_suffix='.tfrecord.gz')
        )