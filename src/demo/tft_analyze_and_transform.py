import argparse
import atexit
import logging
import shutil
import tempfile

import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import StandardOptions
import tensorflow as tf
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata

from demo._common import load_module_from_file_path
from demo._common import load_schema


_logger = logging.getLogger()


def _get_tft_temp_dir(pipeline_options):
    if pipeline_options.view_as(StandardOptions).runner == 'DataflowRunnner':
        tft_temp_dir = pipeline_options.view_as(GoogleCloudOptions).temp_location
    else:
        tft_temp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tft_temp_dir))
    return tft_temp_dir


def _main(argv=None):
    _logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_examples_path', required=True)
    parser.add_argument('--raw_examples_schema_path', required=True)
    parser.add_argument('--preprocessing_module_path', required=True)
    parser.add_argument('--transformed_examples_path_prefix', required=True)
    parser.add_argument('--transform_fn_dir', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    raw_examples_schema = load_schema(known_args.raw_examples_schema_path)
    raw_examples_coder = tft.coders.ExampleProtoCoder(raw_examples_schema)
    raw_examples_metadata = dataset_metadata.DatasetMetadata(raw_examples_schema)    

    tft_preprocessing = load_module_from_file_path(
        'tft_preprocessing', known_args.preprocessing_module_path
    )
    preprocessing_fn = tft_preprocessing.preprocessing_fn
    
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as pipeline:
        with tft_beam.Context(temp_dir=_get_tft_temp_dir(pipeline_options)):
            raw_examples = (
                pipeline
                | 'ReadRawExamples' >> beam.io.ReadFromTFRecord(
                    known_args.raw_examples_path, coder=raw_examples_coder
                )
            )
            raw_dataset = (raw_examples, raw_examples_metadata)
            transformed_dataset, transform_fn = (
                raw_dataset | tft_beam.AnalyzeAndTransformDataset(preprocessing_fn)
            )
            (transformed_examples, transformed_examples_metadata) = transformed_dataset
            transformed_examples_coder = tft.coders.ExampleProtoCoder(
                transformed_examples_metadata.schema
            )
            _ = (
                transformed_examples
                | 'WriteTransformedExamples' >> beam.io.WriteToTFRecord(
                    known_args.transformed_examples_path_prefix,
                    file_name_suffix='.tfrecord.gz',
                    coder=transformed_examples_coder
                )
            )
            _ = (
                transform_fn
                | 'WriteTransformFn' >> tft_beam.WriteTransformFn(known_args.transform_fn_dir)
            )


if __name__ == '__main__':
    _main()