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
    parser.add_argument('--preprocessing_module_path', required=True)
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
        with tft_beam.Context(temp_dir=get_beam_temp_dir(pipeline_options)):
            raw_examples = pipeline | 'ReadRawExamples' >> beam.io.ReadFromTFRecord(
                known_args.raw_examples_path, coder=raw_examples_coder
            )
            raw_examples_dataset = (raw_examples, raw_examples_metadata)
            transform_fn = raw_examples_dataset | tft_beam.AnalyzeDataset(preprocessing_fn)
            transform_fn | 'WriteTransformFn' >> tft_beam.WriteTransformFn(
                known_args.transform_fn_dir
            )


if __name__ == '__main__':
    _main()