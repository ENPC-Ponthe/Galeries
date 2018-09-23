mkdir -p db-backup
docker-compose exec backup /backup.sh
docker-compose build web
docker-compose up -d web
