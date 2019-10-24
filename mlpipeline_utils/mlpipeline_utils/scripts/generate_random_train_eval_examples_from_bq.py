import argparse
import logging
import os
from typing import NamedTuple

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from google.cloud import bigquery
import tensorflow as tf
from tensorflow.python.lib.io import file_io

from mlpipeline_utils._bq_beam_utils import *


def _generate_random_train_eval_examples_from_bq(
    base_query,
    base_sample_rate,
    train_samples_fraction,
    train_output_dir,
    eval_output_dir,
    pipeline_options
):
    sampling_query = f'''
    SELECT * FROM (
        SELECT *, (ABS(FARM_FINGERPRINT(row_id)) / 0x7FFFFFFFFFFFFFFF) AS selection_chance
        FROM ({base_query})
    )
    WHERE selection_chance < {base_sample_rate}
    '''

    row_to_tf_example_converter = BigQueryToTFExampleConverter(sampling_query)

    def train_eval_partition_fn(row, n_partitions):
        return int(row['selection_chance'] > base_sample_rate * train_samples_fraction)

    bookkeeping_columns = ['row_id', 'selection_chance']
    with beam.Pipeline(options=pipeline_options) as pipeline:
        all_samples = pipeline | 'QueryTable' >> beam.io.Read(
            beam.io.BigQuerySource(query=sampling_query, use_standard_sql=True)
        )
        train_samples, eval_samples = all_samples | 'TrainEvalPartition' >> beam.Partition(
            train_eval_partition_fn, 2
        )
        train_samples | "WriteTrainDataset" >> WriteBigQueryRowsToTFRecord(
            row_to_tf_example_converter, train_output_dir, bookkeeping_columns
        )
        eval_samples | "WriteEvalDataset" >> WriteBigQueryRowsToTFRecord(
            row_to_tf_example_converter, eval_output_dir, bookkeeping_columns
        )


def _main(argv=None):
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_query', required=True)
    parser.add_argument('--base_sample_rate', type=float, required=True)
    parser.add_argument('--train_samples_fraction', type=float, required=True)
    parser.add_argument('--output_dir', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    train_output_dir = os.path.join(known_args.output_dir, 'train')
    eval_output_dir = os.path.join(known_args.output_dir, 'eval')

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    _generate_random_train_eval_examples_from_bq(
        base_query=known_args.base_query,
        base_sample_rate=known_args.base_sample_rate,
        train_samples_fraction=known_args.train_samples_fraction,
        train_output_dir=train_output_dir,
        eval_output_dir=eval_output_dir,
        pipeline_options=pipeline_options
    )


if __name__ == '__main__':
    _main()