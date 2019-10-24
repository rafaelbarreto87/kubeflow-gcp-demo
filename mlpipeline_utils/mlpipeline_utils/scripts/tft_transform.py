import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata

from mlpipeline_utils._common import get_beam_temp_dir
from mlpipeline_utils._common import load_module_from_file_path
from mlpipeline_utils._common import load_schema


def _main(argv=None):
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_examples_path', required=True)
    parser.add_argument('--raw_examples_schema_path', required=True)
    parser.add_argument('--transform_fn_dir', required=True)
    parser.add_argument('--transformed_examples_path_prefix', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    raw_examples_schema = load_schema(known_args.raw_examples_schema_path)
    raw_examples_coder = tft.coders.ExampleProtoCoder(raw_examples_schema)
    raw_examples_metadata = dataset_metadata.DatasetMetadata(raw_examples_schema)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as pipeline:
        with tft_beam.Context(temp_dir=get_beam_temp_dir(pipeline_options)):
            transform_fn = pipeline | tft_beam.ReadTransformFn(known_args.transform_fn_dir)
            raw_examples = (
                pipeline
                | 'ReadRawExamples' >> beam.io.ReadFromTFRecord(
                    known_args.raw_examples_path, coder=raw_examples_coder
                )
            )
            raw_examples_dataset = (raw_examples, raw_examples_metadata)
            transformed_examples, transform_examples_metadata = (
                (raw_examples_dataset, transform_fn) | tft_beam.TransformDataset()
            )
            transformed_examples_coder = tft.coders.ExampleProtoCoder(
                transform_examples_metadata.schema
            )
            transformed_examples | 'WriteTransformedExamples' >> beam.io.WriteToTFRecord(
                known_args.transformed_examples_path_prefix,
                file_name_suffix='.tfrecord.gz',
                coder=transformed_examples_coder
            )


if __name__ == '__main__':
    _main()