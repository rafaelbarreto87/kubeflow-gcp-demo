FROM tensorflow/tensorflow:1.14.0-py3

RUN pip install --upgrade --no-cache-dir pip
RUN pip install --upgrade --no-cache-dir setuptools
RUN pip install --upgrade --no-cache-dir \
        apache-beam[gcp]==2.16.0 \
        google-cloud-bigquery==1.17.1 \
        google-cloud-core==1.0.3 \
        google-cloud-storage==1.20.0 \
        kfp==0.1.32 \
        papermill[gcs]==1.2.1 \
        six==1.12.0 \
        tensorflow-data-validation==0.14.1 \
        tensorflow-model-analysis==0.14.0 \
        tensorflow-transform==0.14.0