# C.M.I.
python module to interact and read data from C.M.I. logger from [Technische Alternative](https://www.ta.co.at)

## Install depencies
```sh
$> poetry install
```

## Check source code
```sh
$> poetry run flake8
```

## Build package
```sh
$> poetry build
```

### Export the available data from C.M.I. to a csv file
```sh
$> poetry run cmi/export_csv.py
```

### Transfer C.M.I. data to postgres
```sh
# generate sql schema for later transfer of C.M.I. data to postgresql
$> poetry run cmi/generate_sql_schema.py

# create database and user
$> sudo --user=postgres createuser --no-createdb --no-createrole --no-superuser --pwprompt <USER>
$> sudo --user=postgres createdb --encoding=UTF-8 --owner=<USER> <DATABASE>

# create schema for database
$> cat cmi.sql | psql --host=<HOST> --dbname=<DATABASE> <USER>

# create database connection configuration
$> cat cmi_postgres.txt <<EOF
EOF

$> poetry run cmi/export_postgresql.py
```
