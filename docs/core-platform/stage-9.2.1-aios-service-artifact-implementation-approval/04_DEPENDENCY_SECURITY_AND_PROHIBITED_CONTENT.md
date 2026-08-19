# Dependency, Security, and Prohibited Content

`Wants` and `After` provide soft ordering for network-online and Docker. The unit must not contain `Requires=docker.service`, PostgreSQL container dependencies, `docker compose`, `docker start`, database wait loops, curl/network preflights, or lifecycle commands for PostgreSQL.

The only approved hardening directives are `NoNewPrivileges=true`, `PrivateTmp=true`, and `UMask=0027`. Broader filesystem/capability directives are not authorized.

The artifact must contain zero bot tokens, passwords, DSNs, API keys, test environment variables, file-log destinations, migration/schema commands, monitoring endpoints, Brain/Memory/Specialist references, and runtime data paths inside Git. `EnvironmentFile` is required without a leading optional `-`.

`AIOS_REGISTRY_TEST_DATABASE_URL` is prohibited. Automatic production migration and database modification are prohibited.
