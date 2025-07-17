Bitemporal Django with MariaDB
==============================


System Versioning
-----------------

Model definition to enable `SYSTEM_VERSIONED`:

```python
class Company(Model):
    name = CharField(max_length=255)
    address = CharField(max_length=255)

    class Meta:
        system_versioned = True
```

Querying system versioning:

```python
before = timezone.now()
company = Company.objects.create(name="KFC", address="Hong Kong")
after = timezone.now()
company.address = "New York"
company.save()

# When using a context manager to affect querying, be aware that it will only affect it upon evaluation
queryset = Company.objects.all()

# uses FOR SYSTEM_TIME BETWEEN <before> AND <after> -> New York
with for_system_time(before, after):
    queryset.first().address

# uses FOR SYSTEM_TIME AS OF <before> -> New York
with for_system_time(before):
    queryset.first().address

# uses FOR SYSTEM_TIME ALL -> Hong Kong, New York
with for_sytem_time("all"):
    queryset.values("address")
```

Notes
-----

 - Requires monkey-patching migration autodetector & Meta options
 - Timezone issues when using system versioned AS OF - will need to either:
   - use the time zone of the database; or
   - set the connection to UTC with `set time_zone = '+00:00';`
 - Using a context manager to control the `FOR SYSTEM_TIME` seems like a good idea to set a global rewind time but
   there are subtle behaviour gotchas - if you use the time in the DB backend during compilation then it will only take
   effect during queryset evaluation which means you **will** need to evaluate any querysets before being passed into
   template contexts, otherwise the template rendering will be executed outside the rewind context.
