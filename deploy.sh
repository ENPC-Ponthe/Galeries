mkdir -p db-backup
docker-compose exec backup /backup.sh
docker-compose pull web
docker-compose up -d web
docker-compose exec web flask db upgrade
