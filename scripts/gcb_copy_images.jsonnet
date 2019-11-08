{
  // The newRegistry for the image
  local newRegistry = std.extVar("newRegistry"),

  // A template for defining the steps to retag each image.
  local subGraphTemplate(image) = {
    local imagePieces = std.split(image, "/"),
    local imageName = if std.length(imagePieces) > 1 then
      imagePieces[1:]
      else
      [image],
    local nameAndTag = imageName[std.length(imageName) - 1],

    local template = self,

    local newImage = std.join("/", [newRegistry] +  imageName),

    images+: [newImage],

    local pullName = "pull-" + nameAndTag,
    steps+: [
      {
        id: pullName,
        name: "gcr.io/cloud-builders/docker",
        args: ["pull", image],
        waitFor: ["-"],
      },
      {
        id: "tag-" + nameAndTag,
        name: "gcr.io/cloud-builders/docker",
        args: ["tag", image, newImage],
        waitFor: ["pull-" + nameAndTag],
      },
    ],
  },

  local images = [
    "docker.io/alpine:latest",
    "docker.io/argoproj/argoui:v2.3.0",
    "docker.io/argoproj/workflow-controller:v2.3.0",
    "docker.io/grafana/grafana:6.0.2",
    "docker.io/istio/citadel:1.1.6",
    "docker.io/istio/galley:1.1.6",
    "docker.io/istio/kubectl:1.1.6",
    "docker.io/istio/mixer:1.1.6",
    "docker.io/istio/pilot:1.1.6",
    "docker.io/istio/proxy_init:1.1.6",
    "docker.io/istio/proxyv2:1.1.6",
    "docker.io/istio/sidecar_injector:1.1.6",
    "docker.io/jaegertracing/all-in-one:1.9",
    "docker.io/kiali/kiali:v0.16",
    "docker.io/metacontroller/metacontroller:v0.3.0",
    "docker.io/minio/minio:RELEASE.2018-02-09T22-40-05Z",
    "docker.io/mysql:5.6",
    "docker.io/mysql:8.0.3",
    "docker.io/prom/prometheus:v2.3.1",
    "docker.io/seldonio/seldon-core-operator:0.3.1",
    "docker.io/tensorflow/tensorflow:1.8.0",
    "gcr.io/google_containers/spartakus-amd64:v1.1.0",
    "gcr.io/kubeflow-images-public/admission-webhook:v20190520-v0-139-gcee39dbc-dirty-0d8f4c",
    "gcr.io/kubeflow-images-public/centraldashboard:v0.5.0",
    "gcr.io/kubeflow-images-public/centraldashboard:v20190823-v0.6.0-rc.0-69-gcb7dab59",
    "gcr.io/kubeflow-images-public/ingress-setup:latest",
    "gcr.io/kubeflow-images-public/jupyter-web-app:v0.5.0",
    "gcr.io/kubeflow-images-public/jupyter-web-app:9419d4d",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-controller:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-controller:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-manager-rest:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-manager-rest:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-manager:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-manager:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-ui:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/katib-ui:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/metrics-collector:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-bayesianoptimization:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-bayesianoptimization:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-grid:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-grid:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-hyperband:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-hyperband:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-nasrl:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-nasrl:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-random:v0.1.2-alpha-289-g14dad8b",
    "gcr.io/kubeflow-images-public/katib/v1alpha2/suggestion-random:v0.6.0-rc.0",
    "gcr.io/kubeflow-images-public/kfam:v20190612-v0-170-ga06cdb79-dirty-a33ee4",
    "gcr.io/kubeflow-images-public/kubernetes-sigs/application:1.0-beta",
    "gcr.io/kubeflow-images-public/metadata-frontend:v0.1.8",
    "gcr.io/kubeflow-images-public/metadata:v0.1.8",
    "gcr.io/kubeflow-images-public/notebook-controller:v20190603-v0-175-geeca4530-e3b0c4",
    "gcr.io/kubeflow-images-public/notebook-controller:v20190614-v0-160-g386f2749-e3b0c4",
    "gcr.io/kubeflow-images-public/profile-controller:v20190619-v0-219-gbd3daa8c-dirty-1ced0e",
    "gcr.io/kubeflow-images-public/pytorch-operator:v0.5.1-5-ge775742",
    "gcr.io/kubeflow-images-public/pytorch-operator:v1.0.0-rc.0",
    "gcr.io/kubeflow-images-public/tf_operator:v0.6.0.rc0",
    "gcr.io/ml-pipeline/api-server:0.1.23",
    "gcr.io/ml-pipeline/frontend:0.1.23",
    "gcr.io/ml-pipeline/persistenceagent:0.1.23",
    "gcr.io/ml-pipeline/scheduledworkflow:0.1.23",
    "gcr.io/ml-pipeline/viewer-crd-controller:0.1.23"
  ],

  local steps = std.map(subGraphTemplate, images),

  local combine(l, r) = l+r,
  all: std.foldl(combine, steps, {}),
}.all
