# repobee-feedback
[![Build Status](https://travis-ci.com/repobee/repobee-feedback.svg)](https://travis-ci.com/repobee/repobee-feedback)
[![Code Coverage](https://codecov.io/gh/repobee/repobee-feedback/branch/master/graph/badge.svg)](https://codecov.io/gh/repobee/repobee-feedback)
[![PyPi Version](https://badge.fury.io/py/repobee-feedback.svg)](https://badge.fury.io/py/repobee-feedback)
![Supported Python Versions](https://img.shields.io/badge/python-3.5%7C3.6%7C3.7%7C3.8-blue)
![Supported Platforms](https://img.shields.io/badge/platforms-Linux%2C%20macOS-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A [RepoBee](https://github.com/repobee/repobee) plugin that adds the
`issue-feedback` command to RepoBee. It allows the user to specify a
directory containing _issue files_. Issue files are simply markdown
files in which the first line is taken to be the title of the issue, and the
rest the body. The `issue-feedback` command looks for issue files called
`<STUDENT_REPO_NAME>.md`, and opens them in the respective student repos.

Alternatively, you can also use a special file format to put all issues into
the same file, see [The multi issues file](#the-multi-issues-file).

> **Important:** This plugin is still in very early stages and may change
> considerably over the coming weeks.

## Install
`repobee-feedback` is on PyPi, so installing is as simple as:

```
python3 -m pip install --user --upgrade repobee-feedback
```

If you want the latest dev-build, you can also install directly from the repo:

```
$ python3 -m pip install git+https://github.com/repobee/repobee-feedback.git
```

## Usage

### Activate the plugin
To use `repobee-feedback`, you first need to [install it](#Install), and then
activate it as a plugin. You can do that either by providing it on the command
line:

```
$ repobee -p feedback issue-feedback [...]
```

Or, you can add it to the `plugins` section of the config file.

```
[DEFAULTS]
plugins = feedback
```

And then the `issue-feedback` command will simply appear. For more details on
using plugins, see the
[RepoBee plugin docs](https://repobee.readthedocs.io/en/stable/plugins.html#using-existing-plugins).

### The issue files
`issue-feedback` looks for files called `<STUDENT_REPO_NAME>.md`. So, if you for
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

### Using the `issue-feedback` command
The `issue-feedback` command is straightforward. It takes the "regular" options
that most RepoBee commands (base url, token, etc), but these are also picked
from the config file as per usual. With a typical RepoBee configuration, you
only need to supply `--mn|--master-repo-names` and `-s|--students` (or
`--sf|--students_file`). Here's an example:

```
$ repobee -p feedback issue-feedback --mn task-1 -s slarse rjglasse
```

This will cause `issue-feedback` to search through the current directory (which
is the default issue directory) for `slarse-task-1.md` and `rjglasse-task-1.md`.

> **Note:** By default, `issue-feedback` runs in interactive mode: it will
> prompt you `y/n` before opening an issue. See the next section for how to
> disable that.

### Optional arguments
`issue-feedback` has three optional arguments: `-b|--batch-mode`,
`--id|--issue-dir` and `--mi|--multi-issues-file`.

> **Note:** `--id` and `--mi` are mutually exclusive, you can only supply one.

```
  -b, --batch-mode      Run without any yes/no promts.
  --id ISSUES_DIR, --issues-dir ISSUES_DIR
                        Directory containing issue files. The files should be
                        named <STUDENT_REPO_NAME>.md (for example, slarse-
                        task-1.md). The first line is assumed to be the title,
                        and the rest the body. Defaults to the current
  --mi MULTI_ISSUES_FILE, --multi-issues-file MULTI_ISSUES_FILE
                        File containing all issues to be openend. Each
                        separate issue should begin with a line containing
                        only #ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>. For
                        example, for student `slarse` and assignment `task-1`
                        and issue title `Pass`, the line should read
                        `#ISSUE#slarse-task-1#Pass` (without backticks). The
                        very first line of the file must be an #ISSUE# line.
```

# License
See [LICENSE](LICENSE) for details.
