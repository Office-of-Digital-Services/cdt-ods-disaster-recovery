# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| web/\_\_init\_\_.py                     |        5 |        2 |        0 |        0 |     60% |       5-7 |
| web/core/\_\_init\_\_.py                |        0 |        0 |        0 |        0 |    100% |           |
| web/core/admin/\_\_init\_\_.py          |        2 |        0 |        0 |        0 |    100% |           |
| web/core/admin/userflow.py              |        7 |        0 |        0 |        0 |    100% |           |
| web/core/apps.py                        |        5 |        0 |        0 |        0 |    100% |           |
| web/core/context\_processors.py         |        9 |        9 |        2 |        0 |      0% |      1-12 |
| web/core/middleware.py                  |        9 |        1 |        2 |        1 |     82% |        19 |
| web/core/migrations/0001\_initial.py    |        7 |        7 |        0 |        0 |      0% |      3-17 |
| web/core/migrations/\_\_init\_\_.py     |        0 |        0 |        0 |        0 |    100% |           |
| web/core/models/\_\_init\_\_.py         |        2 |        0 |        0 |        0 |    100% |           |
| web/core/models/userflow.py             |       39 |       15 |        0 |        0 |     62% |68, 72-77, 81-84, 88-91 |
| web/core/session.py                     |        9 |        9 |        2 |        0 |      0% |      1-13 |
| web/core/urls.py                        |        4 |        4 |        0 |        0 |      0% |       1-7 |
| web/oauth/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| web/oauth/admin/\_\_init\_\_.py         |        2 |        0 |        0 |        0 |    100% |           |
| web/oauth/admin/config.py               |        7 |        0 |        0 |        0 |    100% |           |
| web/oauth/apps.py                       |        5 |        0 |        0 |        0 |    100% |           |
| web/oauth/claims.py                     |       24 |       24 |       16 |        0 |      0% |      1-37 |
| web/oauth/client.py                     |       24 |       24 |        6 |        0 |      0% |      5-65 |
| web/oauth/migrations/0001\_initial.py   |        8 |        8 |        0 |        0 |      0% |      3-17 |
| web/oauth/migrations/\_\_init\_\_.py    |        0 |        0 |        0 |        0 |    100% |           |
| web/oauth/models/\_\_init\_\_.py        |        3 |        0 |        0 |        0 |    100% |           |
| web/oauth/models/config.py              |       17 |        3 |        0 |        0 |     82% | 31-32, 35 |
| web/oauth/models/secret\_name\_field.py |       12 |        2 |        0 |        0 |     83% |     30-31 |
| web/oauth/redirects.py                  |       17 |       17 |        2 |        0 |      0% |      1-34 |
| web/oauth/routes.py                     |        9 |        9 |        0 |        0 |      0% |      1-10 |
| web/oauth/secrets.py                    |       48 |       29 |       10 |        1 |     34% |47-82, 86-95 |
| web/oauth/session.py                    |       36 |       36 |        8 |        0 |      0% |      1-65 |
| web/oauth/urls.py                       |       11 |       11 |        4 |        0 |      0% |      1-28 |
| web/oauth/views.py                      |       89 |       89 |       26 |        0 |      0% |     1-152 |
| web/settings.py                         |       60 |        9 |       12 |        3 |     75% |42-49, 94->98, 109->112, 122 |
| web/urls.py                             |        3 |        3 |        0 |        0 |      0% |      8-11 |
| web/vital\_records/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/apps.py              |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/session.py           |       24 |       24 |       10 |        0 |      0% |      1-29 |
| web/vital\_records/urls.py              |        4 |        4 |        0 |        0 |      0% |       1-8 |
| web/vital\_records/views.py             |       13 |       13 |        0 |        0 |      0% |      1-22 |
| web/wsgi.py                             |       14 |       14 |        2 |        0 |      0% |      8-26 |
|                               **TOTAL** |  **533** |  **366** |  **102** |    **5** | **27%** |           |


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