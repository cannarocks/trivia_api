include .env
	
export_db:
	docker exec -t trivia_db_postgresql pg_dumpall -c -U ${POSTGRES_USER} | gzip > ./tmp/dump_$(date +"%Y-%m-%d_%H_%M_%S").gz

reset_api_db:
	docker exec -i trivia_db_postgresql psql -U ${POSTGRES_USER} -c "DROP DATABASE IF EXISTS ${DB_NAME};"
	docker exec -i trivia_db_postgresql psql -U ${POSTGRES_USER} -c "CREATE DATABASE ${DB_NAME};"
	cat trivia.psql | docker exec -i trivia_db_postgresql psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${DB_NAME}"

reset_test_db:
	docker exec -i trivia_db_postgresql psql -U ${POSTGRES_USER} -c "DROP DATABASE IF EXISTS ${DB_TEST};"
	docker exec -i trivia_db_postgresql psql -U ${POSTGRES_USER} -c "CREATE DATABASE ${DB_TEST};"
	cat trivia.psql | docker exec -i trivia_db_postgresql psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${DB_TEST}"

up:
	docker-compose up -d

stop:
	docker-compose stop
	docker-compose down --remove-orphans

application-reload: stop up

application-fresh: application-reload reset_api_db reset_test_db up
