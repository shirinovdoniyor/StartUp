from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'apps_workshop'
                      AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE apps_workshop
                        ADD COLUMN updated_at timestamp with time zone;
                    UPDATE apps_workshop
                        SET updated_at = created_at
                        WHERE updated_at IS NULL;
                    ALTER TABLE apps_workshop
                        ALTER COLUMN updated_at SET DEFAULT now();
                    ALTER TABLE apps_workshop
                        ALTER COLUMN updated_at SET NOT NULL;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'apps_workshop'
                      AND column_name = 'longitude'
                ) THEN
                    ALTER TABLE apps_workshop
                        ADD COLUMN longitude double precision;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'apps_workshop'
                      AND column_name = 'latitude'
                ) THEN
                    ALTER TABLE apps_workshop
                        ADD COLUMN latitude double precision;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'apps_workshop'
                      AND column_name = 'is_active'
                ) THEN
                    ALTER TABLE apps_workshop
                        ADD COLUMN is_active boolean NOT NULL DEFAULT true;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        )
    ]
