# `weather_prog`

A CLI application to store weather forecasts into a csv.

## Configuration

The application can be configured in multiple ways:

- over the shell environment - more in [the docs](https://docs.pydantic.dev/usage/settings/#environment-variable-names)
  - can be archived by creating a `.env` file in the app root
  - with `export $SETTING_NAME=$SETTING_VALUE` before calling the app
- with a [`config.json`](./.weather_prog/config.json) inside the `.weather_prog/` directory
- hardcoded in the [`_settings.py`](./src/weather_prog/_settings.py) file (not recommended)

The settings source priority the app has is:
init_settings, env_settings, json_config_settings_source, file_secret_settings

1. The data inside the `_settings.py`
2. Then the data inside the environment / `.env` file
3. In the `config.json` file
4. Inside the `app/secrets` directory

For certain secret settings (like passwords, username, ips), one can make use of the `pydantic` secrets support.
More info on that [here](https://docs.pydantic.dev/usage/settings/#secret-support).

Basically you create the settings name as the file name and have the value as the only input for that file.

## Development

It is recommended to install [`poetry`](https://python-poetry.org/) to work with this project.
If you are **NOT** using `poetry`, in the app root, you can find the [`requirements.txt`](./requirements.txt) and [`requirements.dev.txt`](./requirements.dev.txt) files to install the projects dependencies.

After that you:

1. install all dependencies

```sh
> poetry install
```

2. check wether [`poe`](https://github.com/nat-n/poethepoet) was installed correctly

```sh
> poetry run poe
```

3. perform any additional setup required automatically

```sh
poetry run poe install
```

From now on, its recommended to use `poe` to call for all you needs.

```sh
> poetry run poe

<...>

CONFIGURED TASKS
  style:check           Check the app code style
  style:fix             Check and auto-fix the app code style
  setup-precommit-hook  Setup the git pre-commit hock that checks for style errors
  install               Install all application dependencies
  test                  Run application tests
```

E.g., run `poetry run poe install` to install all dependencies or `poetry run poe test` to run application tests!

## Run the app

For running the app, one has 2 options:

- `poetry run weather_prog` OR `weather_prog` when installed locally without `poetry`
- `python -m weather_prog` (`-m` = calls a python module)
  - this works if you install the app to your local machine. You can ofc also call this with `poetry run python -m weather_prog`.

## Tooling

We use `poetry` for package management. Package managers have several advantages: Fixed and explicit versioning of dependencies, replication of same circumstances across different machines, ...

To manage development commands, we use [`poe` the poet](https://github.com/nat-n/poethepoet). This has several advantages. For development the main advantage is that there is no need to memorize the commands for all dev tools we use:

- `poetry run poe style:fix` will fix the style for you,
  =- ...

For more `poe` goodness read [their feature overview](https://github.com/nat-n/poethepoet#features).

## FAQ

1. What formatting tools do we use?
   - we use [black](https://github.com/psf/black) for code-formatting
   - we use [isort](https://github.com/PyCQA/isort) for import formatting
   - both can resolve their own errors (for the most part)
   - **pro-tip:** Your code editor likely also supports using both with very little setup
     - VSCode: Open python file -> `CTRL/CMD + SHIFT + P` -> `Format Document` -> When asked select "Black" (instead of autopep8 or yapf or similar)
     - Vim/Nvim with [Neoformat](https://github.com/sbdchd/neoformat) extension: `:Neoformat`
2. What tools do we use for testing?
   - [`flake8`](https://pypi.org/project/flake8/) to lint for common code errors and anti-patterns
   - [`mypy`](http://www.mypy-lang.org/) for typing
   - [`pytest`](https://docs.pytest.org/en/latest/) for writing tests
