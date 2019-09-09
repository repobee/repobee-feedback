# repobee-feedback
A [RepoBee](https://github.com/repobee/repobee) plugin that adds the
`issue-feedback` command to RepoBee. It searches for files in student repos
called `issue.md`, takes the first line of the file as a title and the rest as
a body, and opens it as an issue on the associated student repo's issue
tracker.

> **Important:** This plugin is highly experimental and only tested manually,
> use with caution!

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
The plugin command searches for files that match a certain bash glob pattern
(by default the pattern is simply `issue.md`) in local student repos.

> **Important:** Note _local student repos_. This means that you first need to
> run `repobee clone` for the student repos that you want, and then create issue
> files in these.

The first line of the file is assumed to be the title, and the rest of the file
the body. There must be exactly one file in each repo that matches the pattern,
or the `issue-feedback` command aborts.

### Using the `issue-feedback` command
The `issue-feedback` command is straightforward. It takes the "regular" options
that most RepoBee commands (base url, token, etc), but these are also picked
from the config file as per usual. With a typical RepoBee configuration, you
only need to supply `--mn|--master-repo-names` and `-s|--students` (or
`--sf|--students_file`). Here's an example:

```
$ repobee -p feedback issue-feedback --mn task-1 -s slarse rjglasse tmore
```

This will use search for files matching the default `issue.md` pattern (i.e.
only files called exactly `issue.md`) and open them as issues in the student
repos.

> **Note:** By default, `issue-feedback` runs in interactive mode: it will
> prompt you `y/n` before opening an issue. See the next section for how to
> disable that.

### Optional arguments
`issue-feedback` has two optional arguments: `-b|--batch-mode` and
`-i|--issue-pattern`. Here are the descriptions for them:

```
  -b, --batch-mode      Run without any yes/no promts.
  -i ISSUE_PATTERN, --issue-pattern ISSUE_PATTERN
                        The pattern used to find issue files. Should be a bash
                        pattern (i.e. not regex). Default is 'issue.md'.
```

# License
See [LICENSE](LICENSE) for details.
