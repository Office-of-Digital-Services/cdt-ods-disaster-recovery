# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                      |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------------------------------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| web/\_\_init\_\_.py                                                                       |        5 |        0 |        0 |        0 |    100% |           |
| web/core/\_\_init\_\_.py                                                                  |        0 |        0 |        0 |        0 |    100% |           |
| web/core/admin.py                                                                         |        7 |        0 |        0 |        0 |    100% |           |
| web/core/apps.py                                                                          |        5 |        0 |        0 |        0 |    100% |           |
| web/core/hooks.py                                                                         |       11 |        4 |        0 |        0 |     64% |9-10, 14-15 |
| web/core/management/\_\_init\_\_.py                                                       |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/\_\_init\_\_.py                                              |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/reset\_db.py                                                 |       39 |        0 |        4 |        0 |    100% |           |
| web/core/middleware.py                                                                    |        9 |        1 |        2 |        1 |     82% |        19 |
| web/core/migrations/0001\_initial.py                                                      |        7 |        0 |        0 |        0 |    100% |           |
| web/core/migrations/\_\_init\_\_.py                                                       |        0 |        0 |        0 |        0 |    100% |           |
| web/core/models.py                                                                        |        8 |        0 |        0 |        0 |    100% |           |
| web/core/session.py                                                                       |       19 |        7 |        4 |        1 |     57% |13-19, 25-26, 30-33 |
| web/core/urls.py                                                                          |       11 |        3 |        0 |        0 |     73% |     12-20 |
| web/settings.py                                                                           |       65 |        9 |       12 |        3 |     77% |42-49, 94->98, 109->112, 121 |
| web/urls.py                                                                               |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/\_\_init\_\_.py                                                        |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/apps.py                                                                |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/forms.py                                                               |       62 |       22 |        6 |        0 |     59% |113-120, 123-133, 136-144 |
| web/vital\_records/hooks.py                                                               |       15 |        6 |        0 |        0 |     60% |9-10, 14-15, 19-20 |
| web/vital\_records/migrations/0001\_initial.py                                            |        7 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0002\_vitalrecordsrequest\_legal\_attestation\_and\_more.py |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0003\_vitalrecordsrequest\_first\_name\_and\_more.py        |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0004\_vitalrecordsrequest\_county\_of\_birth\_and\_more.py  |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0005\_vitalrecordsrequest\_date\_of\_birth\_and\_more.py    |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/models.py                                                              |       38 |        6 |        0 |        0 |     84% |112, 116, 120, 124, 128, 132 |
| web/vital\_records/session.py                                                             |       13 |        4 |        2 |        0 |     60% |     15-18 |
| web/vital\_records/urls.py                                                                |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/views.py                                                               |      111 |       41 |        4 |        0 |     61% |45-51, 54, 63-69, 72, 81-87, 90, 99-105, 108, 118-124, 127, 137-146, 149-156, 159-161, 164 |
| web/wsgi.py                                                                               |        6 |        6 |        0 |        0 |      0% |      8-16 |
|                                                                                 **TOTAL** |  **471** |  **109** |   **34** |    **5** | **73%** |           |


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