import pytest
from django.utils import timezone

from .models import Company, Employee, for_system_time

pytestmark = pytest.mark.django_db


def test_system_time_all():
    company = Company.objects.create(name="KFC", address="Melbourne")
    company.address = "Geelong"
    company.save()

    # system time will be set on evaluation when using a context
    qs = Company.objects.all()
    with for_system_time("all"):
        query_string = str(qs.query)
        assert "FOR SYSTEM_TIME ALL" in query_string
        assert list(qs.values("name", "address")) == [
            {
                "name": "KFC",
                "address": "Melbourne",
            },
            {
                "name": "KFC",
                "address": "Geelong",
            },
        ]


def test_system_time_as_of():
    company = Company.objects.create(name="KFC", address="Melbourne")
    company.address = "Geelong"
    company.save()
    now = timezone.now()

    qs = Company.objects.all()
    with for_system_time(now):
        query_string = str(qs.query)
        assert f"FOR SYSTEM_TIME AS OF {now}" in query_string
        assert list(Company.objects.values("name", "address")) == [
            {
                "name": "KFC",
                "address": "Geelong",
            },
        ]


def test_relationships():
    company = Company.objects.create(name="KFC", address="Melbourne")
    Employee.objects.create(name="Fred", company=company)
    now = timezone.now()
    company.address = "Geelong"
    company.save()

    with for_system_time(now):
        employee = Employee.objects.first()
        assert employee.company.address == "Melbourne"


def test_system_time_between():
    start = timezone.now()
    company = Company.objects.create(name="KFC", address="Melbourne")
    end = timezone.now()
    company.address = "Geelong"
    company.save()

    qs = Company.objects.all()
    with for_system_time(start, end):
        query_string = str(qs.query)
        assert f"FOR SYSTEM_TIME BETWEEN {start} AND {end}" in query_string
        assert list(Company.objects.values("name", "address")) == [
            {
                "name": "KFC",
                "address": "Melbourne",
            },
        ]
