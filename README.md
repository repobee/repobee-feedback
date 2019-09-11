# repobee-feedback
A [RepoBee](https://github.com/repobee/repobee) plugin that adds the
`issue-feedback` command to RepoBee. It allows the user to specify a
directory containing _issue files_. Issue files are simply markdown
files in which the first line is taken to be the title of the issue, and the
rest the body. The `issue-feedback` command looks for issue files called
`<STUDENT_REPO_NAME>.md`, and opens them in the respective student repos.

> **Important:** This plugin is still in very early stages and may change
> considerably over the coming weeks.

## Install
As `repobee-feedback` is experimental, it is not on PyPi. You can install it
directly from this repo with:

```
$ python3 -m pip install git+https://github.com/slarse/repobee-feedback.git
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
`issue-feedback` has two optional arguments: `-b|--batch-mode` and
`--id|--issue-dir`. Here are the descriptions for them:

```
  -b, --batch-mode      Run without any yes/no promts.
  --id ISSUES_DIR, --issues-dir ISSUES_DIR
                        Directory containing issue files. The files should be
                        named <STUDENT_REPO_NAME>.md (for example, slarse-
                        task-1.md). The first line is assumed to be the title,
                        and the rest the body. Defaults to the current
```

# License
See [LICENSE](LICENSE) for details.
