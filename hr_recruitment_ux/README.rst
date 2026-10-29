.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
HR Recruitment UX
==================

This module adds:

* Automatically archives an applicant when adding it to a talent pool creates a new talent,
  and logs an internal note with the pools, the job position and the stage.
  Applicants already directly linked to a talent are not archived.
* Per-vacancy rotting SLA: allows configuring specific "days to rot" on each job position,
  overriding the stage threshold when needed. When enabled on a stage, applicants of a
  configured position use the position's threshold instead of the stage's.

Installation
============

To install this module, you need to:

#. Just install this module

Configuration
=============

To configure this module, you need to:

#. Nothing to configure

Usage
=====

To use this module, you need to:

#. In debug mode, go to Recruitment > Configuration > Job Positions > Stages and open a stage.
#. Enable "¿Días para deteriorarse por posición?" and add the job positions with their days to rot.

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

This module is maintained by ADHOC SA.

To contribute to this module, please visit https://www.adhoc.com.ar.
