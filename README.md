# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                  |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| web/\_\_init\_\_.py                   |        5 |        2 |        0 |        0 |     60% |       5-7 |
| web/core/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| web/core/apps.py                      |        5 |        0 |        0 |        0 |    100% |           |
| web/core/middleware.py                |        9 |        1 |        2 |        1 |     82% |        19 |
| web/core/models.py                    |       12 |        2 |        0 |        0 |     83% |     30-31 |
| web/core/urls.py                      |        4 |        4 |        0 |        0 |      0% |       1-7 |
| web/oauth/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| web/oauth/admin.py                    |        7 |        0 |        0 |        0 |    100% |           |
| web/oauth/apps.py                     |        5 |        0 |        0 |        0 |    100% |           |
| web/oauth/client.py                   |       21 |       21 |        4 |        0 |      0% |      5-62 |
| web/oauth/migrations/0001\_initial.py |        8 |        8 |        0 |        0 |      0% |      3-15 |
| web/oauth/migrations/\_\_init\_\_.py  |        0 |        0 |        0 |        0 |    100% |           |
| web/oauth/models.py                   |       18 |        3 |        0 |        0 |     83% | 37-38, 41 |
| web/oauth/redirects.py                |       17 |       17 |        2 |        0 |      0% |      1-34 |
| web/oauth/routes.py                   |        9 |        9 |        0 |        0 |      0% |      1-10 |
| web/oauth/session.py                  |       16 |       16 |        4 |        0 |      0% |      1-29 |
| web/oauth/urls.py                     |       11 |       11 |        4 |        0 |      0% |      1-27 |
| web/oauth/views.py                    |       98 |       98 |       32 |        0 |      0% |     1-169 |
| web/secrets.py                        |       48 |       29 |       10 |        1 |     34% |47-82, 86-95 |
| web/settings.py                       |       53 |        8 |       10 |        2 |     75% |42-49, 94->98, 109->112 |
| web/urls.py                           |        3 |        3 |        0 |        0 |      0% |      8-11 |
| web/vital\_records/\_\_init\_\_.py    |        0 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/apps.py            |        5 |        0 |        0 |        0 |    100% |           |
| web/vital\_records/urls.py            |        4 |        4 |        0 |        0 |      0% |       1-7 |
| web/wsgi.py                           |        4 |        4 |        0 |        0 |      0% |      8-14 |
|                             **TOTAL** |  **362** |  **240** |   **68** |    **4** | **29%** |           |


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