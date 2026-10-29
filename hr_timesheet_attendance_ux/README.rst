.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=======================
Attendance Timesheet UX
=======================

#. Add link from timesheets to timesheet vs attendance analysis
#. Timesheets/All Timesheets odoo menu is set visible only in developer mode.
#. When you set the employee or the date of a timesheet, the time spent is
   suggested: the attendance hours of that day in the user's timezone (open
   attendances count up to now), minus the break, minus the time already
   logged that day. Timesheets from time off requests are not counted as
   already logged.
#. The task selector of a timesheet does not offer tasks in a folded stage or
   template tasks.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Nothing to configure

Usage
=====

To use this module, you need to:

#. Go to Timesheets > Timesheets > My Timesheet / Attendance to compare your
   attendance time with your timesheets, day by day.
#. Create a timesheet and check the suggested time spent.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
