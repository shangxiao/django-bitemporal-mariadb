import threading
from contextlib import contextmanager

from django.db import models

#
# ✓ customise DEFAULT_NAMES - monkey patch
# ✓ customise backend schema editor to append WITH SYSTEM VERSIONING
# - migrations to detect when remove system_versioned attr or flip from True to False
# - custom operation to alter table add system versioning
#


class SystemTime(threading.local):
    for_from = None
    for_to = None

    def __repr__(self):
        return f"{self.for_from} → {self.for_to}"


system_time = SystemTime()


@contextmanager
def for_system_time(timestamp_from, timestamp_to=None):
    system_time.for_from = timestamp_from
    system_time.for_to = timestamp_to
    yield
    system_time.for_from = None
    system_time.for_to = None


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    class Meta:
        system_versioned = True

    def __str__(self):
        return self.name + " - " + self.address


class Employee(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        system_versioned = True

    def __str__(self):
        return self.name
