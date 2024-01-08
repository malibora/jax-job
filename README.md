## JaxJob CompositeController

This is a [CompositeController](https://metacontroller.github.io/metacontroller/api/compositecontroller.html) suitable for running a distributed training jobs in K8s. The difference between the "JaxJob" controller compared to other training operators like MPIOperator and PyTorchOperator is that:
-  It does not have a launcher and worker pods, but only worker pods, which is in suitable for Jax framework.
- When any of the workers fail, all worker pods will be restarted. This is suitable for distributed wokloads with checkpointing.


```yaml
apiVersion: nebius.ai/v1
kind: JaxJob
metadata:
  name: jax-job
  labels:
    app: jax
  annotations:
    jax-job-label: jax
spec:
  parallelism: 7
  template:
    metadata:
      labels:
        app: jax
    spec:
      containers:
      - #Your container spec
...
```


### Prerequisites

* Kubernetes 1.8+ is recommended for its improved CRD support,
  especially garbage collection.
* Install [Metacontroller](https://github.com/metacontroller/metacontroller).

### Deploy the CompositeController

```sh
kubectl apply -k manifest
```

### Create an Example Job

```sh
kubectl apply -f my-job.yaml
```
