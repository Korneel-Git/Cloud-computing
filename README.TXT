
git clone https://github.com/Korneel-Git/Cloud-computing.git
cd Cloud-computing
Copy-Item .env.example .env


docker compose up -d --build
docker compose ps
curl.exe http://localhost:8000/health

Open http://localhost:8000 in je browser.


docker compose down
