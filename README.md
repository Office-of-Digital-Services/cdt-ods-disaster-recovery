# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                                      |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| web/\_\_init\_\_.py                                                                                       |        5 |        0 |        0 |        0 |    100% |           |
| web/core/\_\_init\_\_.py                                                                                  |        0 |        0 |        0 |        0 |    100% |           |
| web/core/admin.py                                                                                         |        7 |        0 |        0 |        0 |    100% |           |
| web/core/apps.py                                                                                          |        5 |        0 |        0 |        0 |    100% |           |
| web/core/hooks.py                                                                                         |       11 |        4 |        0 |        0 |     64% |9-10, 14-15 |
| web/core/management/\_\_init\_\_.py                                                                       |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/\_\_init\_\_.py                                                              |        0 |        0 |        0 |        0 |    100% |           |
| web/core/management/commands/ensure\_db.py                                                                |      125 |        0 |       30 |        2 |     99% |144->146, 208->212 |
| web/core/middleware.py                                                                                    |        9 |        1 |        2 |        1 |     82% |        19 |
| web/core/migrations/0001\_initial.py                                                                      |        7 |        0 |        0 |        0 |    100% |           |
| web/core/migrations/\_\_init\_\_.py                                                                       |        0 |        0 |        0 |        0 |    100% |           |
| web/core/models.py                                                                                        |        8 |        0 |        0 |        0 |    100% |           |
| web/core/session.py                                                                                       |       25 |        5 |        4 |        2 |     76% |13-19, 25-26, 33 |
| web/core/tasks.py                                                                                         |       15 |        6 |        0 |        0 |     60% |53-56, 60, 64 |
| web/core/urls.py                                                                                          |        4 |        0 |        0 |        0 |    100% |           |
| web/core/views.py                                                                                         |        9 |        0 |        2 |        0 |    100% |           |
| web/settings.py                                                                                           |       74 |       12 |       14 |        4 |     75% |42-49, 95->99, 110->113, 122, 224-226 |
| web/urls.py                                                                                               |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/\_\_init\_\_.py                                                                        |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/apps.py                                                                                |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/forms.py                                                                               |       83 |       22 |        6 |        0 |     69% |113-120, 123-133, 136-144 |
| web/vital\_records/hooks.py                                                                               |       16 |        6 |        0 |        0 |     62% |10-11, 15-16, 20-21 |
| web/vital\_records/migrations/0001\_initial.py                                                            |        7 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0002\_vitalrecordsrequest\_legal\_attestation\_and\_more.py                 |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0003\_vitalrecordsrequest\_first\_name\_and\_more.py                        |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0004\_vitalrecordsrequest\_county\_of\_birth\_and\_more.py                  |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0005\_vitalrecordsrequest\_date\_of\_birth\_and\_more.py                    |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0006\_vitalrecordsrequest\_parent\_1\_first\_name\_and\_more.py             |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0007\_vitalrecordsrequest\_address\_vitalrecordsrequest\_city\_and\_more.py |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0008\_vitalrecordsrequest\_enqueued\_at\_and\_more.py                       |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/0009\_vitalrecordsrequest\_started\_at\_and\_more.py                        |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/migrations/\_\_init\_\_.py                                                             |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/models.py                                                                              |       78 |       14 |        0 |        0 |     82% |202-203, 207, 211, 215, 219, 223, 227, 231-232, 236, 240, 244, 248 |
| web/vital\_records/routes.py                                                                              |       17 |        1 |        0 |        0 |     94% |        20 |
| web/vital\_records/session.py                                                                             |       13 |        4 |        2 |        0 |     60% |     15-18 |
| web/vital\_records/tasks.py                                                                               |       99 |       44 |        6 |        0 |     52% |52-53, 57-66, 74, 77-117, 120-126, 134, 137-156, 161-167 |
| web/vital\_records/templatetags/\_\_init\_\_.py                                                           |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/templatetags/form\_helpers.py                                                          |       10 |       10 |        2 |        0 |      0% |      1-13 |
| web/vital\_records/urls.py                                                                                |        4 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/views.py                                                                               |      141 |       64 |        6 |        0 |     52% |52-57, 67-72, 82-87, 90-98, 108-113, 124-129, 139-144, 147-158, 168-173, 176-183, 193-202, 205-212, 215-217, 226-237 |
| web/wsgi.py                                                                                               |        6 |        6 |        0 |        0 |      0% |      8-16 |
|                                                                                                 **TOTAL** |  **827** |  **199** |   **74** |    **9** | **74%** |           |


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