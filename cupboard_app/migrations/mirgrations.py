from django.db import migrations
# Ignore migrations for Mongo
class Migration(migrations.Migration):
    def apply(self, project_state, schema_editor, collect_sql=False):
        pass

    def unapply(self, project_state, schema_editor, collect_sql=False):
        pass