# Walkthrough Of Develoment

This is an attempt to quickly document the process of developing this library, and the corresponding Home Assistant integration.

## Home Assistant

Home Assistant is maintained in their main GitHub branch [here](https://github.com/home-assistant/core). In order to make changes, you will have to fork that repository to your own account, then create a branch off of that fork, and then make your changes to that branch.

The changes you make will have to comply with Home Assistant's extensive guidelines before they will accept them into the main codebase. The guidelines can all be found [here](https://developers.home-assistant.io/).

### Development

The easiest way to do development on HA is to set up a dev container with VSCode. It is simple to set up, and it creates a docker container that runs locally, and gets automatically loaded with all the dependencies and requirements to run Home Assistant. HA has good documentation on how to set up a dev container [here](https://developers.home-assistant.io/docs/development_environment).

For a better idea of the architecture of HA integrations, see [here](https://developers.home-assistant.io/docs/architecture_components)

If you already have a core integration to work on, it will be located at `homeassistant/components/<integration name>`. If you don't, you will need to create a folder here to hold your integration. THe folder should be named the same name that you will use as your domain for the rest of development, which should be a simplified version of the name of the product you are creating the integration for.

You can run your altered code in several ways. The easiest is to do what they say in the documentation above using Tasks to run it in the docker container. This will allow you to make sure your code compiles and runs, but will have limited network connectivity, and no access to hardware devices. If you want to test your code on running Home Assistant instance (like one on a raspberry pi) you will have to use it as a "custom integration".

To use your integration as a custom integration, you will need to download the code from your dev container, and put it into the `\config\custom_components` folder on the machine running HA. You will also need to modify the manifest.py file, and add a version field. Without this field, HA will not allow a custom integration to run, but if this field is included, it will not allow a core integration to run, so it has to be added manually any time you want to run a core integration as a custom. something like `"version":"0.1.0"` will work fine.

If you ever make changes to the strings.json file, you will have to update the `\translations\en.json` file. This file is automatically generated from the strings.json file when you run Home Assistant in the dev container, or you can update it manually by copying the contents of strings.json into en.json.

While working on your integration, if you make changes to the VegeHub package that is hosted on PyPi (this package), you will need to publish the changes to PyPi (see [here](#publishing-this-library)), then you will need to change the package version in your integration's `mainfest.py` file, then you will usually want to run `pip install vegehub -U` in the terminal of the HA dev container, so that it pulls the latest version of the package.

Testing the integration can be done by running the command `pytest ./tests/components/vegehub/ --cov=homeassistant.components.vegehub --cov-report term-missing -vv` in the dev container. Sometimes you will have to update the snapshots first if you have made changes to the sensors. The command for that is `pytest tests/components/vegehub/test_sensor.py --snapshot-update`

### Committing

Before submitting your code, in the dev container you will want to open a terminal so that you can run `python3 -m script.gen_requirements_all`, which updates the HA system to include any resources your integration requires, and `python3 -m script.hassfest`, which updates the HA internals so that they will see your integration. These are documented in the [development checklist](https://developers.home-assistant.io/docs/development_checklist).

The dev container has several checks, including: mypy (type checking), ruff (linting), and prettier (formatting), built in to automatically run when you commit your code. The system won't let you commit until all failures are resolved.

You will also want to write/run unit tests. HA uses pytest, and has good documentation on how to use it [here](https://developers.home-assistant.io/docs/development_testing)

### Submitting

Once you have completed your changes, and committed the code to your branch, you can create a Pull Request (PR) to request to get your code included in the main repository code.

Most people in tech fields already know git really well, but I had to learn this stuff from scratch, so PRs were another thing I had to figure out. Briefly: you fill out their template and submit it, and then someone has to review the changes you've made in order to confirm that everything you've done is correct. If they find anything wrong, they will request changes, you make the changes, and commit your code, and the PR is automatically updated with the changes. When your all changes are complete, hit "Ready for review" on your PR to inform a reviewer that it needs to be checked again.

You can also set a PR to be a draft, which still makes it show up in the list of PRs for the project, but lets people know that there are problems with it that you are working on. In HA, the system automatically marks your PR as a draft whenever you have changes that need to be made, so you might need to double check that it isn't still set as a draft if you are waiting for a review.

HA also does not ever allow you to ask people for reviews or mention anyone by name in order to get their attention drawn to your PR.

## Further Reading

HA has excellent documentation on all of this, and much more, [here](https://developers.home-assistant.io/).

## Publishing this library

This project uses [Poetry](https://python-poetry.org/) for dependency management and publishing. Make sure that poetry is installed before continuing.

If you haven't set up this project, you will need to run `poetry install` in the base directory. That will install all dependencies and set up a virtual environment automatically.

For convenience, you may want to change the Python interpreter to the virtual environment created by Poetry so that VSCode isn't constantly telling you that it can't find your imports. To do this, use the command `poetry env info` to see the virtual environment info or `poetry env info --path` to directly get the path to the environment. Then hit `ctrl+shift+p` to enter the command prompt for VSCode, start typing `Python: Select Interpreter` and click that when it comes up. In there you should have the option to enter the path to the interpreter you want to use, click that, and enter the path to the Poetry virtual environment.

Before publishing this library be sure to run the following commands:

- `poetry run pylint vegehub`
- `poetry run mypy vegehub`
- `poetry run pytest --cov=vegehub tests/ --cov-report term-missing -vv`
  - Make sure that the tests have 100% coverage of the code.

Then, if all those pass, change the version number in `pyproject.toml`, and run:

- `poetry build`

Now you can publish to PyPi by running

- `poetry publish`

If that fails, you might need to take care of authentication first. You will have to get on PyPi and get an API key, then run `poetry config pypi-token.pypi <your-api-token>`, then run `poetry publish` again.

It looks like it's also possible for the API token to get messed up. It is located in `/home/user/.config/pypoetry/auth.toml` and I had a problem where poetry kept failing to publish, even after inputting the API token multiple times and trying multiple tokens. I went to this file to check that the token was there, and it turned out it was only saving part of the token for some reason. Still not sure why. And also not sure why how it got altered from its previous working state.

And don't forget to commit to GitHub.
