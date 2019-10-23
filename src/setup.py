from setuptools import find_packages
from setuptools import setup


_REQUIRED_PACKAGES=[
    'tensorflow-transform==0.14.0'
]


setup(
    name='kubeflow-gcp-demo',
    description='Demo of capabilities of Kubeflow on GCP.',
    url='https://github.com/rafaelbarreto87/kubeflow-gcp-demo',
    author='Rafael Barreto',
    author_email='rafaelbarreto87@gmail.com',
    version='0.1',
    install_requires=_REQUIRED_PACKAGES,
    include_package_data=True,
    packages=find_packages(),
)