(Bi)Temporal Django with MariaDB
================================


Notes
-----

 - Requires monkey-patching migration autodetector & Meta options
 - Timezone issues when using system versioned AS OF - will need to either:
   - use the time zone of the database; or
   - set the connection to UTC with `set time_zone = '+00:00';`
