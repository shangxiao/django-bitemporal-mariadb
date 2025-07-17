from django.apps import AppConfig
from django.core.management.commands import makemigrations, migrate
from django.db.migrations import state
from django.db.models import options

from bitemporal.db_backend.migrations import MigrationAutodetectorMixin

if "system_versioned" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES += ("system_versioned",)

if "system_versioned" not in state.DEFAULT_NAMES:
    state.DEFAULT_NAMES += ("system_versioned",)


if not issubclass(  # pragma: no branch
    makemigrations.MigrationAutodetector, MigrationAutodetectorMixin
):
    makemigrations.MigrationAutodetector = type(
        "MigrationAutodetector",
        (MigrationAutodetectorMixin, makemigrations.MigrationAutodetector),
        {},
    )

if not issubclass(  # pragma: no branch
    migrate.MigrationAutodetector, MigrationAutodetectorMixin
):
    migrate.MigrationAutodetector = type(
        "MigrationAutodetector",
        (MigrationAutodetectorMixin, migrate.MigrationAutodetector),
        {},
    )


makemigrations.Command.autodetector = makemigrations.MigrationAutodetector
migrate.Command.autodetector = makemigrations.MigrationAutodetector


class CleanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clean"
