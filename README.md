# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                   |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| web/\_\_init\_\_.py                                                                    |        5 |        2 |        0 |        0 |     60% |       5-7 |
| web/core/\_\_init\_\_.py                                                               |        0 |        0 |        0 |        0 |    100% |           |
| web/core/admin.py                                                                      |       24 |       13 |        2 |        0 |     42% |     21-39 |
| web/core/apps.py                                                                       |        5 |        0 |        0 |        0 |    100% |           |
| web/core/hooks.py                                                                      |       11 |        4 |        0 |        0 |     64% |9-10, 14-15 |
| web/core/management/\_\_init\_\_.py                                                    |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/\_\_init\_\_.py                                           |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/ensure\_db.py                                             |      183 |        4 |       42 |        4 |     96% |73, 87-89, 99, 103->exit, 230->232, 306->310 |
| web/core/middleware.py                                                                 |        9 |        1 |        2 |        1 |     82% |        19 |
| web/core/migrations/0001\_initial.py                                                   |        7 |        0 |        0 |        0 |    100% |           |
| web/core/migrations/\_\_init\_\_.py                                                    |        0 |        0 |        0 |        0 |    100% |           |
| web/core/models.py                                                                     |        8 |        0 |        0 |        0 |    100% |           |
| web/core/session.py                                                                    |       25 |        5 |        4 |        2 |     76% |13-19, 25-26, 33 |
| web/core/tasks.py                                                                      |       15 |        2 |        0 |        0 |     87% |    60, 64 |
| web/core/urls.py                                                                       |        5 |        0 |        0 |        0 |    100% |           |
| web/core/views.py                                                                      |        9 |        0 |        2 |        0 |    100% |           |
| web/monitoring.py                                                                      |       12 |        0 |        4 |        0 |    100% |           |
| web/settings.py                                                                        |      108 |        6 |       14 |        7 |     89% |52, 54, 56, 127->131, 139->142, 151, 267-268 |
| web/urls.py                                                                            |       16 |        7 |        2 |        1 |     56% |     31-39 |
| web/vital\_records/\_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/admin.py                                                            |        6 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/apps.py                                                             |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/forms/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/forms/birth.py                                                      |       24 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/forms/common.py                                                     |       75 |       22 |        6 |        0 |     65% |249-256, 259-269, 272-280 |
| web/vital\_records/forms/marriage.py                                                   |       21 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/hooks.py                                                            |       16 |        6 |        0 |        0 |     62% |10-11, 15-16, 20-21 |
| web/vital\_records/migrations/0001\_initial.py                                         |        7 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0002\_model\_updates\_marriage\_flow.py                  |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0003\_alter\_vitalrecordsrequest\_status.py              |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0004\_alter\_vitalrecordsrequest\_fire\_relationship.py  |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0005\_vitalrecordsrequest\_middle\_names.py              |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0006\_alter\_vitalrecordsrequest\_status.py              |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0007\_alter\_vitalrecordsrequest\_number\_of\_records.py |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0008\_alter\_vitalrecordsrequest\_choices.py             |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/mixins.py                                                           |       74 |        2 |       12 |        1 |     94% |     13-14 |
| web/vital\_records/models.py                                                           |       86 |        6 |        4 |        0 |     93% |88, 92, 96, 100, 104, 108 |
| web/vital\_records/routes.py                                                           |       27 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/session.py                                                          |       26 |        0 |        6 |        0 |    100% |           |
| web/vital\_records/tasks/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/tasks/cleanup.py                                                    |       68 |        0 |       18 |        0 |    100% |           |
| web/vital\_records/tasks/email.py                                                      |       33 |        2 |        0 |        0 |     94% |     29-34 |
| web/vital\_records/tasks/package.py                                                    |      152 |        0 |        6 |        1 |     99% |  224->228 |
| web/vital\_records/tasks/utils.py                                                      |        7 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/templatetags/\_\_init\_\_.py                                        |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/templatetags/form\_helpers.py                                       |       10 |       10 |        2 |        0 |      0% |      1-13 |
| web/vital\_records/urls.py                                                             |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/views/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/views/birth.py                                                      |       58 |       33 |        0 |        0 |     43% |16-28, 36-47, 54-60, 71-90 |
| web/vital\_records/views/common.py                                                     |      150 |       53 |        6 |        0 |     62% |60-63, 87-92, 95-98, 108-112, 115-122, 154-162, 174-182, 185-192, 195-200, 208-210, 214-225 |
| web/vital\_records/views/death.py                                                      |       14 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/views/marriage.py                                                   |       39 |       26 |        0 |        0 |     33% |10-36, 44-57, 64-70 |
| web/wsgi.py                                                                            |        6 |        6 |        0 |        0 |      0% |      8-16 |
|                                                                              **TOTAL** | **1380** |  **210** |  **132** |   **17** | **84%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FOffice-of-Digital-Services%2Fcdt-ods-disaster-recovery%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.