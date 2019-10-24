import argparse
from contextlib import redirect_stdout
import io
import json
import logging
import os

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from tensorflow.python.lib.io import file_io
import tensorflow_data_validation as tfdv


_logger = logging.getLogger()


def _generate_stats(known_args, pipeline_args):
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    stats_output_path = os.path.join(known_args.output_dir, 'stats.tfrecord')
    stats = tfdv.generate_statistics_from_tfrecord(
        known_args.data_location,
        output_path=stats_output_path,
        pipeline_options=pipeline_options
    )
    file_io.write_string_to_file('/tmp/stats_output_path.txt', stats_output_path)
    return stats


def _write_stats_visualization(output_dir, stats):
    stats_viz_output_path = os.path.join(output_dir, 'stats_viz.html')
    stats_viz_rendered_html = tfdv.utils.display_util.get_statistics_html(stats)
    file_io.write_string_to_file(stats_viz_output_path, stats_viz_rendered_html)
    file_io.write_string_to_file('/tmp/stats_viz_output_path.txt', stats_viz_output_path)
    return stats_viz_output_path


def _infer_schema(output_dir, stats):
    inferred_schema_output_path = os.path.join(output_dir, 'inferred_schema.pb2')
    inferred_schema = tfdv.infer_schema(stats)
    file_io.write_string_to_file(inferred_schema_output_path, inferred_schema.SerializeToString())
    file_io.write_string_to_file(
        '/tmp/inferred_schema_output_path.txt', inferred_schema_output_path
    )
    return inferred_schema


def _render_inferred_schema_summary_markdown(inferred_schema):
    display_schema_out = io.StringIO()
    with redirect_stdout(display_schema_out):
        tfdv.display_schema(inferred_schema)
    return f'''# Inferred schema summary
```
{display_schema_out.getvalue()}
```'''


def _write_mlpipeline_ui_metadata(stats_viz_output_path, inferred_schema):
    metadata_as_json = json.dumps({
        'outputs': [
            {
                'type': 'web-app',
                'storage': 'gcs',
                'source': stats_viz_output_path,
            },
            {
                'storage': 'inline',
                'source': _render_inferred_schema_summary_markdown(inferred_schema),
                'type': 'markdown',
            },
        ]
    })
    file_io.write_string_to_file('/tmp/mlpipeline-ui-metadata.json', metadata_as_json)


def _main(argv=None):
    _logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_location', required=True)
    parser.add_argument('--output_dir', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    stats = _generate_stats(known_args, pipeline_args)
    stats_viz_output_path = _write_stats_visualization(known_args.output_dir, stats)
    inferred_schema = _infer_schema(known_args.output_dir, stats)
    _write_mlpipeline_ui_metadata(stats_viz_output_path, inferred_schema)


if __name__ == '__main__':
    _main()