from datetime import datetime

from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from django.db.backends.mysql.compiler import (
    SQLAggregateCompiler,
)
from django.db.backends.mysql.compiler import SQLCompiler as BaseSQLCompiler
from django.db.backends.mysql.compiler import (
    SQLDeleteCompiler,
    SQLInsertCompiler,
    SQLUpdateCompiler,
)
from django.db.backends.mysql.operations import (
    DatabaseOperations as BaseDatabaseOperations,
)
from django.db.backends.mysql.schema import (
    DatabaseSchemaEditor as MySQLDatabaseSchemaEditor,
)
from django.db.models.sql.datastructures import BaseTable

from clean.models import system_time

__all__ = [
    "SQLAggregateCompiler",
    "SQLCompiler",
    "SQLDeleteCompiler",
    "SQLInsertCompiler",
    "SQLUpdateCompiler",
]


class SQLCompiler(BaseSQLCompiler):
    def compile(self, node):
        sql, params = super().compile(node)
        if (
            isinstance(node, BaseTable)
            and getattr(self.query.model._meta, "system_versioned", False)
            and system_time.for_from is not None
        ):
            if system_time.for_to is not None:
                sql += " FOR SYSTEM_TIME BETWEEN %s AND %s"
                params += [system_time.for_from, system_time.for_to]
            elif isinstance(system_time.for_from, datetime):
                sql += " FOR SYSTEM_TIME AS OF %s"
                params += [system_time.for_from]
            elif system_time.for_from == "all":
                sql += " FOR SYSTEM_TIME ALL"
        return sql, params


class DatabaseSchemaEditor(MySQLDatabaseSchemaEditor):
    def table_sql(self, model):
        sql, params = super().table_sql(model)
        if getattr(model._meta, "system_versioned", False):
            sql += " WITH SYSTEM VERSIONING"
        return sql, params

    def add_system_versioning(self, model):
        table_name = self.quote_name(model._meta.db_table)
        sql = f"ALTER TABLE {table_name} ADD SYSTEM VERSIONING"
        self.execute(sql)

    def remove_system_versioning(self, model):
        table_name = self.quote_name(model._meta.db_table)
        sql = f"ALTER TABLE {table_name} DROP SYSTEM VERSIONING"
        self.execute(sql)


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "bitemporal.db_backend.base"


class DatabaseWrapper(MySQLDatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
    ops_class = DatabaseOperations
