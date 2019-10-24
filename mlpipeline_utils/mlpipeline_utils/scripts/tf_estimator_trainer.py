import argparse
import json
import logging
import os
import re

import tensorflow as tf
from tensorflow.python.lib.io import file_io
import tensorflow_model_analysis as tfma

from mlpipeline_utils._common import load_module_from_file_path


_logger = logging.getLogger()


def _write_mlpipeline_metrics(all_metrics, metrics_to_export):
    if metrics_to_export is not None:
        metrics_to_export = set(metrics_to_export)
    exported_metrics = []
    for metric_name, metric_value in all_metrics.items():
        if metrics_to_export is not None and metric_name not in metrics_to_export:
            continue
        exported_metrics.append({
            'name': re.sub('[^a-z0-9]', '-', metric_name.lower()),
            'numberValue':  float(metric_value),
        })
    metrics_as_json = json.dumps({'metrics': exported_metrics})
    file_io.write_string_to_file('/tmp/mlpipeline-metrics.json', metrics_as_json)
    _logger.info(f'mlpipeline-metrics.json written: {metrics_as_json}')


def _write_mlpipeline_ui_metadata(model_dir):
    metadata_as_json = json.dumps({
        'outputs': [
            {
                'type': 'tensorboard',
                'source': model_dir,
            }
        ]
    })
    file_io.write_string_to_file(
        '/tmp/mlpipeline-ui-metadata.json',
        metadata_as_json
    )
    _logger.info(f'mlpipeline-ui-metadata.json written: {metadata_as_json}')


def _main(argv=None):
    _logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--module_path', required=True)
    parser.add_argument('--model_dir', type=str, required=True)
    parser.add_argument('--metrics_to_export', metavar='N', nargs='*')
    parser.add_argument('--hparams', type=json.loads, default={})
    args = parser.parse_args(argv)

    trainer_mod = load_module_from_file_path('trainer', args.module_path)
    trainer_cfg = trainer_mod.trainer_fn(
        hparams=tf.contrib.training.HParams(**{
            'model_dir': args.model_dir,
            **args.hparams
        })
    )
    metrics, savedmodel_dirs = tf.estimator.train_and_evaluate(
        estimator=trainer_cfg['estimator'],
        train_spec=trainer_cfg['train_spec'],
        eval_spec=trainer_cfg['eval_spec']
    )
    _logger.info(f'Final evaluation metrics: {metrics}')
    _logger.info(f'Exported model directories: {savedmodel_dirs}')
    if 'eval_input_receiver_fn' in trainer_cfg:
        eval_savedmodel_dir = tfma.export.export_eval_savedmodel(
            estimator=trainer_cfg['estimator'],
            export_dir_base=os.path.join(args.model_dir, 'eval_export'),
            eval_input_receiver_fn=trainer_cfg['eval_input_receiver_fn']
        )
        _logger.info(f'Exported eval model directory: {eval_savedmodel_dir}')
        file_io.write_string_to_file(
            '/tmp/eval_savedmodel_dir.txt', eval_savedmodel_dir.decode()
        )
    file_io.write_string_to_file(
        '/tmp/savedmodel_dirs.txt', b'\n'.join(savedmodel_dirs or []).decode()
    )
    _write_mlpipeline_ui_metadata(args.model_dir)
    _write_mlpipeline_metrics(metrics or {}, args.metrics_to_export)


if __name__ == '__main__':
    _main()