##############################################################################
#
#    Copyright (C) 2026  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Website HR Recruitment UX",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "summary": "Fixes phone field validation in the public job application form",
    "depends": [
        "hr_recruitment_ux",
        "website_hr_recruitment",
    ],
    "data": [
        "views/website_hr_recruitment_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_hr_recruitment_ux/static/src/interactions/hr_recruitment_form.js",
        ],
    },
    "auto_install": True,
    "installable": True,
    "application": False,
}
