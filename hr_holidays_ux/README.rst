.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============
Holidays UX
============

This module:

#. Splits time off records by month: a request that spans several months is saved as one time off per month, both when it is created and when its dates are changed.
#. Adds a Pre-Approved stage for time off types that expect a supporting document. When a manager approves a request that has no document yet, it goes to Pre-Approved; once the employee uploads the document, the manager approves it for good.
#. Adds a Pre-Approved filter to the time off search view.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Go to Time Off > Configuration > Time Types and open a type.
#. Check Supporting Document Expected and then Pre Approved Instance.

Usage
=====

To use this module, you need to:

#. An employee requests time off of a type configured with Pre Approved Instance, without a document.
#. A Time Off Officer or the employee's time off manager approves it: the request goes to Pre-Approved.
#. The employee attaches the supporting document in the chatter of the request.
#. The officer or manager clicks Approve: the request is approved.

If the document is already attached when the request is approved, it skips Pre-Approved.

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
