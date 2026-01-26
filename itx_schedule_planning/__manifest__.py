# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "ITX Schedule Planning",
    "summary": "Workforce Schedule Planning for 24/7 Operations",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "ITX",
    "license": "AGPL-3",
    "depends": [
        "hr",
        "resource",
        "hr_attendance",
        "hr_holidays",
        "mail",
        "web_timeline",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # "security/security.xml",

        # Data - Master Data (order matters: pattern before template, workrole before workteam)
        "data/itx.schedule.shift.type.csv",
        "data/itx.schedule.workoff.pattern.csv",
        "data/itx.schedule.planning.template.csv",
        "data/itx.employee.workrole.csv",
        "data/itx.employee.workteam.csv",

        # Demo/Test Data (for timeline testing)
        "data/demo_data.xml",

        # Views - Extensions
        "views/hr_employee_views.xml",

        # Views - Master Data
        "views/workteam_views.xml",
        "views/workrole_views.xml",
        "views/workoff_pattern_views.xml",
        "views/shift_type_views.xml",
        "views/period_views.xml",
        "views/planning_template_views.xml",

        # Views - Core (3 Levels) - order matters: entry -> workrole -> planning
        "views/schedule_planning_workrole_entry_views.xml",
        "views/schedule_planning_workrole_views.xml",
        "views/schedule_planning_views.xml",

        # Menus
        "views/menuitems.xml",

        # Wizards
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
