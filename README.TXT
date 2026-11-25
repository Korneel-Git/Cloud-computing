Cloud Computing
Repository clonen

git clone https://github.com/Korneel-Git/Cloud-computing.git

cd Cloud-computing

Secret aanmaken

Maak een kopie van het voorbeeldbestand:

copy k8s\secret.example.yaml k8s\secret.yaml

Vul daarna de waarden in secret.yaml in.

Vereisten

Ingress-NGINX moet geïnstalleerd zijn op het cluster.

Deployment

Maak een namespace aan:

kubectl create namespace proef

Deploy alle resources:

kubectl apply -f k8s/ -n proef

Controleer of alles correct draait:

kubectl get all -n proef

Hostnaam

Voeg volgende regel toe aan het hosts-bestand van Windows:

127.0.0.1 storingsmelder.local

Open daarna in de browser:

http://storingsmelder.local

Bewijs

De map bewijs bevat een screenshot waaruit blijkt dat de data behouden blijft nadat de PostgreSQL-pod verwijderd en opnieuw aangemaakt wordt.

GitHub Actions

Bij elke push naar de main branch wordt automatisch een nieuwe Docker-image gebouwd en gepusht naar GitHub Container Registry (GHCR).

Opruimen

kubectl delete namespace proef