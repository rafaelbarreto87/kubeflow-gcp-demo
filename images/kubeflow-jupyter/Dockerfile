FROM gcr.io/kubeflow-images-public/tensorflow-1.13.1-notebook-cpu:v0.5.0

USER root
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
ENV SHELL /bin/bash

RUN conda update -n base conda
RUN conda install -c conda-forge nodejs
RUN pip install pip --upgrade --no-cache-dir
RUN pip install setuptools --upgrade --no-cache-dir
RUN pip install jupyterlab --upgrade --no-cache-dir
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
RUN conda clean -tipsy

USER ${NB_USER}

CMD ["bash", "-c", "jupyter lab --notebook-dir=/home/${NB_USER} --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]