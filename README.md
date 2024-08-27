## Fast Zero

#### Activate virtual env

```
source "$( poetry env info --path )/bin/activate"
```

#### Run

```
task run
```

#### Create migration

```
alembic revision --autogenerate -m "<message>"
```

#### Apply migrations

```
alembic upgrade head
```