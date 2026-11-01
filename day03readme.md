Create the folder and namespace

cd ~/projects/gke-sre-ml-platform
mkdir -p k8s/day3
cat > k8s/day3/namespace.yaml <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: day3
EOF
cat k8s/day3/namespace.yaml


Create the service
cat > k8s/day3/service.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: day3
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
EOF
cat k8s/day3/service.yaml


Create the deployment

This is the longest file, so paste it on its own. YAML is sensitive to spacing, so check the output after.

cat > k8s/day3/deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: day3
  labels:
    app: web
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
EOF
cat k8s/day3/deployment.yaml


Compare the cat output with what you typed. If the terminal garbled it, there will be missing lines or stray > characters. If so, press Ctrl+C and paste it again.

;;;;;;;;;;;;;;;;;;;;;;;;;;;partA of day03;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;




Step 1: connect
cd ~/projects/gke-sre-ml-platform/infra/gcp
$(terraform output -raw get_credentials)
kubectl get nodes
cd ~/projects/gke-sre-ml-platform

Step 2: deploy
kubectl apply -f k8s/day3/namespace.yaml
kubectl apply -f k8s/day3/
kubectl get all -n day3
kubectl get pods -n day3 -o wide

You should see 3 pods named web-..., a ReplicaSet, the Deployment and the web Service. The -o wide output shows which node each pod landed on. Note whether they’re spread across both nodes or on one.


Step 3: read what Kubernetes knows
kubectl describe deployment web -n day3 | head -40

Find the StrategyType, RollingUpdateStrategy and Replicas lines. They match your YAML.

Step 4: prove it serves traffic
kubectl port-forward svc/web 8080:80 -n day3

Leave that running, open a second terminal, and run:
curl -s localhost:8080 | head -5


Checking a stale kubeconfig after a cluster rebuild.
Checking a stale kubeconfig after a cluster rebuild.
This is a stale kubeconfig. The new cluster has the same name as yesterday’s, but it has a new certificate authority, and your kubeconfig still holds the old cluster’s certificate. Refresh the entry:

$(terraform output -raw get_credentials)
kubectl config current-context
kubectl get nodes


The first command re-fetches the endpoint and certificate for the new cluster and overwrites the old entry. The context should read gke_srevert-sri023_asia-south1-a_sre-ml-gke.
If it still fails:

kubectl config get-contexts
kubectl config delete-context gke_srevert-sri023_asia-south1-a_sre-ml-gke
kubectl config delete-cluster gke_srevert-sri023_asia-south1-a_sre-ml-gke
$(terraform output -raw get_credentials)
kubectl get nodes

That removes the old entry completely and recreates it.
