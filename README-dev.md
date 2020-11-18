# Installing to virtualenv
In the pipenv/poetry era one would already forget these commands...

```bash
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

# Running tests

Most of the tests are end-to-end - connecting to real sites (not mocked). So one has to configure his/her office/sharepoint credentials. To do so, create a file ```.env``` like this (replace the bracketed values by your values):

```
export Office365_Python_Sdk_SecureVars='{username};{password};{client_id};{client_password}'
export COMPANY={your_company}
```

This file is in .gitignore, so it will never be committed.

```bash
$ . .env   # source it to export the variable
$ nose2 ...  # run the test(s) you need...
```

# Configure Tenant

