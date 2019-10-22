import argparse
import logging
import os

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from google.cloud import bigquery
import tensorflow as tf


_logger = logging.getLogger()


class _BigQueryToTFExampleConverter:

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
                        bytes_list=tf.train.BytesList(value=[tf.compat.as_bytes(s) for s in repeated_value])
                    )
                else:
                    raise RuntimeError(
                        'BigQuery column type {} is not supported.'.format(data_type)
                    )
        return tf.train.Example(features=tf.train.Features(feature=feature))


def _main(argv=None):
    _logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--query',
                        dest='query',
                        required=True,
                        help='The query used to generate the examples.')
    parser.add_argument('--output_dir',
                        dest='output_dir',
                        required=True,
                        help='Directory to write results to.')
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    to_tf_example = _BigQueryToTFExampleConverter(known_args.query)    
    output_prefix = os.path.join(known_args.output_dir, 'part')

    with beam.Pipeline(options=pipeline_options) as pipeline:
        (pipeline
            | 'QueryTable' >> beam.io.Read(beam.io.BigQuerySource(query=known_args.query, use_standard_sql=True))
            | 'ToTFExampleDemo' >> beam.Map(to_tf_example)
            | 'SerializeDeterministically' >> beam.Map(lambda x: x.SerializeToString(deterministic=True))
            | 'Shuffle' >> beam.transforms.Reshuffle()
            | 'WriteToTFRecord' >> beam.io.WriteToTFRecord(output_prefix, file_name_suffix='.tfrecord.gz')
        )


if __name__ == '__main__':
    _main()