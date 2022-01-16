# repobee-feedback
[![Build Status](https://github.com/repobee/repobee-feedback/actions/workflows/tests.yml/badge.svg)](https://github.com/repobee/repobee-feedback/actions/workflows/tests.yml)
[![Code Coverage](https://codecov.io/gh/repobee/repobee-feedback/branch/master/graph/badge.svg)](https://codecov.io/gh/repobee/repobee-feedback)
[![PyPi Version](https://badge.fury.io/py/repobee-feedback.svg)](https://badge.fury.io/py/repobee-feedback)
![Supported Python Versions](https://img.shields.io/badge/python-3.7%7C3.8-blue)
![Supported Platforms](https://img.shields.io/badge/platforms-Linux%2C%20macOS-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **repobee-feedback v0.6.0 requires RepoBee 3:** As of `repobee-feedback`
> v0.6.0, RepoBee 3+ is required.

A [RepoBee](https://github.com/repobee/repobee) plugin that adds the
`feedback` to to RepoBee's `issues` category. It allows the user to specify a
directory containing _issue files_. Issue files are simply markdown files in
which the first line is taken to be the title of the issue, and the rest the
body. The `feedback` command looks for issue files called
`<STUDENT_REPO_NAME>.md`, and opens them in the respective student repos.

Alternatively, you can also use a special file format to put all issues into
the same file, see [The multi issues file](#the-multi-issues-file).

> **How is `feedback` different from `issues open`?** The ``issues open``
> command opens the same issue in all student repositories, while the
> ``feedback`` action allows for unique issues to be opened in each repository.

## Install
Use RepoBee's plugin manager to install.

```bash
$ repobee plugin install
```

## Usage
When active, the `feedback` plugin adds the `feedback` action to the `issues` category.
We recommend activating the `feedback` plugin persistently with `repobee plugin
activate`, such that the action is always available. See the [RepoBee plugin
docs](https://repobee.readthedocs.io/en/stable/plugins.html#using-existing-plugins)
for general information on how to use installed plugins, including activation
and deactivation. The rest of this section assumes that the `feedback` plugin has
been activated persistently.

### The issue files
`feedback` looks for files called `<STUDENT_REPO_NAME>.md`. So, if you for
example want to open feedback issues for students `slarse` and `rjglasse` for
assignment `task-1`, it will expect the files `slarse-task-1.md` and
`rjglasse-task-1.md` to be present in the issue files directory. More files can
be present, but if any of the expected issue files are missing, an error is
displayed and no issues are opened.

The issue files should be Markdown-formatted. **The first line of the file is
the title, the rest is the body.** Note that the title (i.e. first line) should
not contain any formatting as it typically does not render well on
GitHub/GitLab.

### The multi issues file
Alternatively, you can put all issues into a single file and specify the path
to it with the `--multi-issues-file` argument (see [Optional
arguments](#optional-arguments)). Each issue should begin with
`#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>`, and everything between that line
and the next such line is considered to be the body of the issue. Here is an
example file with issues for students `slarse` and `rjglasse` for assignment
`task-1`.

```
#ISSUE#slarse-task-1#This is a neat title
Well done mr slarse, you did good here.
You could have done a bit better on blabla, though.

Overall well done!

#ISSUE#rjglasse-task-1#This is another title
Hmm, not sure what's going on here.

Could you explain it better?
```

> **Note:** The first line of the multi issues file must be an `#ISSUE#` line.

### Using the `feedback` command
The `feedback` command is straightforward. It takes the "regular" options
that most RepoBee commands (base url, token, etc), but these are also picked
from the config file as per usual. With a typical RepoBee configuration, you
only need to supply `-a|--assignments` and `-s|--students` (or
`--sf|--students_file`). Here's an example:

```
$ repobee issues feedback -a task-1 -s slarse rjglasse
```

This will cause `feedback` to search through the current directory (which
is the default issue directory) for `slarse-task-1.md` and `rjglasse-task-1.md`.

> **Note:** By default, `feedback` runs in interactive mode: it will
> prompt you `y/n` before opening an issue. See the next section for how to
> disable that.

Refer to the `feedback` action's help section for details on additional CLI options.

```
$ repobee issues feedback --help
```

## License
See [LICENSE](LICENSE) for details.
