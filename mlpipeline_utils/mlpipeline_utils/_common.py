import atexit
import importlib
import shutil
import tempfile
import uuid

from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import StandardOptions
from tensorflow.python.lib.io import file_io
from tensorflow_metadata.proto.v0 import schema_pb2


def get_beam_temp_dir(pipeline_options):
    if pipeline_options.view_as(StandardOptions).runner == 'DataflowRunner':
        temp_dir = pipeline_options.view_as(GoogleCloudOptions).temp_location
    else:
        temp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(temp_dir))
    return temp_dir


def load_module_from_file_path(module_name_prefix, module_file_path):
    module_uid = str(uuid.uuid4()).replace('-', '')
    module_name = f'{module_name_prefix}_{module_uid}'
    with file_io.FileIO(module_file_path, mode='r') as src_module_fid:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as dst_module_fid:
            dst_module_fid.write(src_module_fid.read())
            dst_module_fid.flush()
            module_spec = importlib.util.spec_from_file_location(module_name, dst_module_fid.name)
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
    return module


def load_schema(schema_pb2_path):
    schema = schema_pb2.Schema()
    schema.ParseFromString(file_io.read_file_to_string(schema_pb2_path, binary_mode=True))
    return schema