# Recover Zulip database

This script recovers Zulip PostgreSQL database, which is no longer readable, due to a disk or power failure.

In particular, this method deals with the following scenario:

1. Some files of /var/lib/postgres/data are missing
2. The latest backup is several months old

Let **destination** database be the older database backup, which shall receive the SQL dump rescued from the corrupted **source** database.

## Preparation

1. Make the source database loadable by copying the missing files from the backup, or creating zero-sized stubs.
2. Create two archives `data_src.tar.gz` and `data_dst.tar.gz`, with source and destination databases, respectively. 

## Recovery

Perform recovery by running the Python script:

```
./zulip-postgres-recovery.py
```

## Troublesooting

1. `fts_update_log relation does not exist`

According to the PostgreSQL rules, the name of function needs to be fully qualified. The workaround was to edit the function via:

```
zulip=# \ef zulip.append_to_fts_update_log
```

and change `fts_update_log` into `zulip.fts_update_log`.

2. `orjson.JSONDecodeError: Input is a zero-length, empty document: line 1 column 1 (char 0)`

Replace the problematic code of file `./zerver/lib/message.py` with the following fragment:

```
        # Render topic_links with the stream's realm instead of the
        # sender's realm; this is important for messages sent by
        # cross-realm bots like NOTIFICATION_BOT.
        obj[TOPIC_LINKS] = topic_links(rendering_realm_id, topic_name)

        if last_edit_time is not None:
            obj["last_edit_timestamp"] = datetime_to_timestamp(last_edit_time)
            assert edit_history_json is not None
            try:
                edit_history: List[EditHistoryEvent] = orjson.loads(edit_history_json)
                obj["edit_history"] = edit_history
            except:
                pass
            finally:
                last_edit_time = None

```

And restart the zulip server by running `supervisorctl restart zulip-django`.

3. After populating older database with recovered content, the `id` still holds the old value:

```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "zerver_usermessage_pkey"``
DETAIL:  Key (id)=(103322) already exists.
```

Solution is to change the `id` value in the database manually:

```
ALTER SEQUENCE zerver_usermessage_id_seq RESTART WITH 123951;
```

