# Cloud Computing

## Repository clonen

```bash
git clone https://github.com/Korneel-Git/Cloud-computing.git
cd Cloud-computing
```

## Kubernetes deployment

Maak een nieuwe namespace aan:

```bash
kubectl create namespace proef
```

Deploy de applicatie en de database:

```bash
kubectl apply -f k8s/ -n proef
```

Controleer of alle resources correct zijn aangemaakt:

```bash
kubectl get all -n proef
```

## Applicatie openen

Maak een port-forward naar de service:

```bash
kubectl port-forward service/storingsmelder 8000:80 -n proef
```

Open daarna de applicatie in je browser:

```text
http://localhost:8000
```

## Opruimen

Verwijder alle resources door de namespace te verwijderen:

```bash
kubectl delete namespace proef
```