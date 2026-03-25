.PHONY: db-shell db-dump db-restore db-reset

# Connect to the PostgreSQL interactive shell
db-shell:
	docker exec -it postgres psql -U postgres -d sansevieria

# Dump the entire database to a SQL file
db-dump:
	docker exec -t postgres pg_dump -U postgres -d sansevieria > sansevieria_dump.sql
	@echo "Database dumped to sansevieria_dump.sql"

# Restore the database from a SQL file
db-restore:
	cat sansevieria_dump.sql | docker exec -i postgres psql -U postgres -d sansevieria
	@echo "Database restored from sansevieria_dump.sql"

# Drop the database schema securely and restart backend (triggers migration & seed natively)
db-reset:
	docker exec -it postgres psql -U postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker compose restart backend
	@echo "Database cleanly reset. Migrations and seed scripts will automatically re-run."
