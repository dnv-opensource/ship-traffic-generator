.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/dnv-opensource/ship-traffic-generator/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* The version of Python (and Conda) that you are using.
* Any additional details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Traffic Generator could always use more documentation, whether as part of the
official Traffic Generator docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/dnv-opensource/ship-traffic-generator/issues. 

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `trafficgen` for local development.

1. Clone the `trafficgen` repo on GitHub.
2. Install your local copy into a pyenv or conda environment.
3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 --config tox.ini ./src/trafficgen ./tests
    $ pytest ./tests
    $ tox

   If you installed the package with `poetry`
    
    $ poetry install --with dev,docs
    
   flake8, pytest and tox should already be installed in your Python environment.
   Note that the tox config assumes Python 3.10 and Python 3.11, you would have
   to have them both available to tox for all tests to run.
   If you only have one of these available tox will skip the non supported
   environment (and in most cases that is OK).
   If you are managing your Python enhancements with `pyenv` you will have to
   install the necessary versions and then run `pyenv rehash` to make them
   available to tox (or set multiple local envs with `pyenv local py310 py311`).
   If you are using `conda` you will have to create a new environment with
   the necessary Python version, install `virtualenv` in the environments
   and then run `conda activate <env-name>` to make it available to tox (to run all
   the environments in one go do `conda activate` inside activated environments).
   
   You can also run the python tests from VSCode via the "Testing" view,
   "Configure Python Tests", with `pytest`` and select the folder `tests`.

5. Commit your changes and push your branch to the source repo::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

6. Submit a pull request through https://github.com/dnv-opensource/ship-traffic-generator/pulls.


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.10.
   

Tips
----

To run a subset of tests::

$ pytest tests.test_trafficgen



Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags
