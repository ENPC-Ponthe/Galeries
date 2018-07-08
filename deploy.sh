mkdir -p db-backup
docker-compose exec backup /backup.sh
docker-compose up -d --build web
