from django.core.management import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Migrate data from the app using the old name `dublinstandup` in postgres"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self._cursor = connection.cursor()

    @property
    def cursor(self):
        return self._cursor

    def handle(self, *args, **options):
        try:
            self.migrate()
        except RuntimeError as err:
            raise CommandError("Unable to move the data\n{0}".format(err))

    def migrate(self):
        with self.cursor:
            if self.is_data_present("standup_pivot"):
                raise RuntimeError("Cowardly refusing to migrate - data exists in target tables")
            if self.does_table_exist('dublinstandup_pivot'):
                self.stdout.write("Migrating data from the pivot table")
                self.migrate_pivots()
            else:
                raise RuntimeError("Unable to find `dublinstandup` app tables")
            if self.does_table_exist('dublinstandup_schedule'):
                self.stdout.write("Migrating data from the schedule table")
                self.migrate_schedule()
            elif self.does_table_exist('dublinstandup_standup'):
                self.stdout.write("Migrating data from the standup table")
                self.migrate_standup()
            else:
                raise RuntimeError("Unable to find `dublinstandup` app tables")

    def does_table_exist(self, table_name):
        self.stdout.write("Checking for presence of the `{0}` table".format(table_name))
        self.cursor.execute("select count(*) from information_schema.tables where table_name like %s", (table_name,))
        row = self.cursor.fetchone()
        return (row is not None) and (row[0] == 1)

    def does_column_exist(self, table_name, column_name):
        self.stdout.write("Checking for presence of {0}.{1}".format(table_name, column_name))
        self.cursor.execute(
            "select count(*) from information_schema.columns where table_name like %s and column_name like %s",
            (table_name, column_name))

    def is_data_present(self, table_name):
        self.cursor.execute("select count(*) from {0}".format(table_name))
        row = self.cursor.fetchone()
        return row[0] > 0

    def migrate_pivots(self):
        if self.does_column_exist("dublinstandup_pivots", "has_left_the_office"):
            self.cursor.execute("insert into standup_pivot select * from dublinstandup_pivot")
        else:
            self.cursor.execute("""insert into standup_pivot(id, full_name, email, slack_handle, has_left_the_office) 
                    select id, full_name, email, slack_handle, false from dublinstandup_pivot""")
        self.stdout.write("{0} row(s) moved".format(self.cursor.rowcount))

    def migrate_schedule(self):
        self.cursor.execute("insert into standup_standup select * from dublinstandup_schedule")
        self.stdout.write("{0} row(s) moved".format(self.cursor.rowcount))

    def migrate_standup(self):
        self.cursor.execute("insert into standup_standup select * from dublinstandup_standup")
        self.stdout.write("{0} row(s) moved".format(self.cursor.rowcount))
