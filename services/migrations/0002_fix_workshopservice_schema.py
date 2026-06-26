from django.db import migrations


def forwards(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'services_workshopservice'
        """)
        columns = {row[0] for row in cursor.fetchall()}

        has_service_name = 'service_name' in columns
        has_service_id = 'service_id' in columns

        if has_service_id and not has_service_name:
            cursor.execute(
                "ALTER TABLE services_workshopservice ADD COLUMN service_name varchar(255);"
            )
            cursor.execute(
                """
                UPDATE services_workshopservice ws
                SET service_name = s.name
                FROM services_service s
                WHERE ws.service_id = s.id
                """
            )
            cursor.execute(
                "ALTER TABLE services_workshopservice ALTER COLUMN service_name SET NOT NULL;"
            )
            cursor.execute(
                "ALTER TABLE services_workshopservice DROP COLUMN service_id;"
            )
        elif has_service_id and has_service_name:
            cursor.execute(
                "ALTER TABLE services_workshopservice DROP COLUMN service_id;"
            )

        cursor.execute("DROP TABLE IF EXISTS services_service CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS services_problem CASCADE;")


def backwards(apps, schema_editor):
    # Intentionally left blank. This migration repairs legacy schema drift.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
