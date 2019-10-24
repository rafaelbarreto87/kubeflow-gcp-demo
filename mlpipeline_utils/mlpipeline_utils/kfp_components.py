import kfp


@kfp.dsl.component
def generate_random_train_eval_examples_from_bq_comp(
    name: str,
    utils_image: str,
    project_id: str,
    region: str,
    temp_dir: str,
    base_query: str,
    base_sample_rate: float,
    train_samples_fraction: float,
    output_dir: str,
    runner: str='DirectRunner'
):
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.generate_random_train_eval_examples_from_bq'],
        arguments=[
            '--runner', runner,
            '--project', project_id,
            '--region', region,
            '--temp_location', temp_dir,
            '--setup_file', './setup.py',
            '--base_query', base_query,
            '--base_sample_rate', base_sample_rate,
            '--train_samples_fraction', train_samples_fraction,
            '--output_dir', output_dir,
        ]
    )


@kfp.dsl.component
def tfrecord_stats_gen_comp(
    name: str,
    utils_image: str,
    project_id: str,
    region: str,
    temp_dir: str,
    data_location: str,
    output_dir: str,
    runner: str='DirectRunner'
) -> {'stats_output_path': str,
      'stats_viz_output_path': str}:
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.tfrecord_stats_gen'],
        arguments=[
            '--runner', runner,
            '--project', project_id,
            '--region', region,
            '--temp_location', temp_dir,
            '--setup_file', './setup.py',
            '--data_location', data_location,
            '--output_dir', output_dir,
        ],
        file_outputs={
            'stats_output_path': '/tmp/stats_output_path.txt',
            'stats_viz_output_path': '/tmp/stats_viz_output_path.txt',
            'inferred_schema_output_path': '/tmp/inferred_schema_output_path.txt'
        },
        output_artifact_paths={
            'mlpipeline-ui-metadata': '/tmp/mlpipeline-ui-metadata.json'
        }
    )


@kfp.dsl.component
def tft_analyze_and_transform_comp(
    name: str,
    utils_image: str,
    project_id: str,
    region: str,
    temp_dir: str,
    raw_examples_path: str,
    raw_examples_schema_path: str,
    preprocessing_module_path: str,
    transformed_examples_path_prefix: str,
    transform_fn_dir: str,
    runner: str='DirectRunner'
):
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.tft_analyze_and_transform'],
        arguments=[
            '--runner', runner,
            '--project', project_id,
            '--region', region,
            '--temp_location', temp_dir,
            '--setup_file', './setup.py',
            '--raw_examples_path', raw_examples_path,
            '--raw_examples_schema_path', raw_examples_schema_path,
            '--preprocessing_module_path', preprocessing_module_path,
            '--transformed_examples_path_prefix', transformed_examples_path_prefix,
            '--transform_fn_dir', transform_fn_dir
        ],
    )


@kfp.dsl.component
def tft_analyze_comp(
    name: str,
    utils_image: str,
    project_id: str,
    region: str,
    temp_dir: str,
    raw_examples_path: str,
    raw_examples_schema_path: str,
    preprocessing_module_path: str,
    transform_fn_dir: str,
    runner: str='DirectRunner'
):
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.tft_analyze'],
        arguments=[
            '--runner', runner,
            '--project', project_id,
            '--region', region,
            '--temp_location', temp_dir,
            '--setup_file', './setup.py',
            '--raw_examples_path', raw_examples_path,
            '--raw_examples_schema_path', raw_examples_schema_path,
            '--preprocessing_module_path', preprocessing_module_path,
            '--transform_fn_dir', transform_fn_dir
        ],
    )


@kfp.dsl.component
def tft_transform_comp(
    name: str,
    utils_image: str,
    project_id: str,
    region: str,
    temp_dir: str,
    raw_examples_path: str,
    raw_examples_schema_path: str,
    transformed_examples_path_prefix: str,
    transform_fn_dir: str,
    runner: str='DirectRunner'
):
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.tft_transform'],
        arguments=[
            '--runner', runner,
            '--project', project_id,
            '--region', region,
            '--temp_location', temp_dir,
            '--setup_file', './setup.py',
            '--raw_examples_path', raw_examples_path,
            '--raw_examples_schema_path', raw_examples_schema_path,
            '--transformed_examples_path_prefix', transformed_examples_path_prefix,
            '--transform_fn_dir', transform_fn_dir
        ],
    )


@kfp.dsl.component
def tf_estimator_trainer_comp(
    name: str,
    utils_image: str,
    module_path: str,
    model_dir: str,
    hparams: str,
    metrics_to_export: str
) -> {'savedmodel_dirs': str, 'eval_savedmodel_dir': str}:
    return kfp.dsl.ContainerOp(
        name=name,
        image=utils_image,
        command=['python3', '-m', 'mlpipeline_utils.scripts.tf_estimator_trainer'],
        arguments=[
            '--module_path', module_path,
            '--model_dir', model_dir,
            '--hparams', hparams,
            '--metrics_to_export',
        ] + metrics_to_export.split(' '),
        file_outputs={
            'savedmodel_dirs': '/tmp/savedmodel_dirs.txt',
            'eval_savedmodel_dir': '/tmp/eval_savedmodel_dir.txt',
        },
        output_artifact_paths={
            'mlpipeline-ui-metadata': '/tmp/mlpipeline-ui-metadata.json',
            'mlpipeline-metrics': '/tmp/mlpipeline-metrics.json'
        }
    )