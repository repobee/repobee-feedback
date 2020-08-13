"""An extension command for RepoBee that looks for files called issue.md in
student repos and opens them as issues on the issue tracker.

.. module:: feedback
    :synopsis: A RepoBee plugin that finds issue files in student repos and
        opens them on their issue trackers

.. moduleauthor:: Simon Larsén
"""
import pathlib
import re
import sys
import argparse
from typing import Iterable, Tuple, List

import daiquiri
import repobee_plug as plug

PLUGIN_NAME = "feedback"

LOGGER = daiquiri.getLogger(__file__)

BEGIN_ISSUE_PATTERN = r"#ISSUE#(.*?)#(.*)"


def callback(args: argparse.Namespace, api: plug.PlatformAPI) -> None:
    repo_name_to_team = {
        plug.generate_repo_name(
            student_team.name, master_repo_name
        ): student_team
        for student_team in args.students
        for master_repo_name in args.master_repo_names
    }
    repo_names = list(repo_name_to_team.keys())

    if "multi_issues_file" in args and args.multi_issues_file is not None:
        issues_file = pathlib.Path(args.multi_issues_file).resolve()
        all_issues = _parse_multi_issues_file(issues_file)
    else:
        issues_dir = pathlib.Path(args.issues_dir).resolve()
        all_issues = _collect_issues(repo_names, issues_dir)

    issues = _extract_expected_issues(
        all_issues, repo_names, args.allow_missing
    )
    for repo_name, issue in issues:
        open_issue = args.batch_mode or _ask_for_open(
            issue, repo_name, args.truncation_length
        )
        if open_issue:
            repo = api.get_repo(repo_name, repo_name_to_team[repo_name])
            api.create_issue(issue.title, issue.body, repo)
        else:
            LOGGER.info("Skipping {}".format(repo_name))


class Feedback(plug.Plugin, plug.cli.Command):
    __settings__ = plug.cli.command_settings(
        help="issue feedback to students",
        description="Collect issues from specified ´issue files´ "
        "to create issues in students repos.",
        category=plug.cli.CoreCommand.issues,
        action="feedback",
    )

    allow_missing = plug.cli.flag(
        help="Emit a warning (instead of crashing) on missing issues.",
    )
    batch_mode = plug.cli.flag(
        short_name="-b", help="Run without any yes/no promts.",
    )
    truncation_length = plug.cli.option(
        short_name="--tl",
        help=(
            "In interactive mode, truncates the body of an issue at this "
            "many characters. If not specified, issue bodies are shown in "
            "full."
        ),
        converter=int,
        default=sys.maxsize,
    )

    group_mutex = plug.cli.mutually_exclusive_group(
        issues_dir=plug.cli.option(
            short_name="--id",
            help=(
                "Directory containing issue files. The files should be "
                "named <STUDENT_REPO_NAME>.md (for example, "
                "slarse-task-1.md). The first line is assumed to be the "
                "title, and the rest the body. Defaults to the current "
                "directory."
            ),
            converter=pathlib.Path,
            default=".",
        ),
        issues_grp=plug.cli.option(
            short_name="--mi",
            help=(
                "File containing all issues to be openend. Each separate "
                "issue should begin with a line containing only "
                "#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>. For example, for "
                "student `slarse` and assignment `task-1` and issue title "
                "`Pass`, the line should read `#ISSUE#slarse-task-1#Pass` "
                "(without backticks). The very first line of the file must "
                "be an #ISSUE# line."
            ),
            converter=pathlib.Path,
        ),
        __required__=True,
    )

    def command(self, api: plug.PlatformAPI):
        callback(self.args, api)


def _ask_for_open(issue: plug.Issue, repo_name: str, trunc_len: int) -> bool:
    LOGGER.info(
        'Processing issue "{}" for {}: {}{}'.format(
            issue.title,
            repo_name,
            issue.body[:trunc_len],
            "[...]" if len(issue.body) > trunc_len else "",
        )
    )
    return (
        input(
            'Open issue "{}" in repo {}? (y/n) '.format(issue.title, repo_name)
        )
        == "y"
    )


def _extract_expected_issues(
    repos_and_issues, repo_names, allow_missing
) -> List[Tuple[str, plug.Issue]]:
    expected_repo_names = set(repo_names)
    expected_repos_and_issues = [
        (repo_name, issue)
        for repo_name, issue in repos_and_issues
        if repo_name in expected_repo_names
    ]
    missing_repos = expected_repo_names - set(
        (repo_name for repo_name, _ in expected_repos_and_issues)
    )
    if missing_repos:
        msg = "Missing issues for: " + ", ".join(missing_repos)
        if allow_missing:
            LOGGER.warning(msg)
        else:
            raise plug.PlugError(msg)

    return expected_repos_and_issues


def _collect_issues(
    repo_names: Iterable[str], issues_dir: pathlib.Path
) -> Iterable[Tuple[str, plug.Issue]]:
    issues = []
    for repo_name in repo_names:
        expected_file = issues_dir / "{}.md".format(repo_name)
        if expected_file.is_file():
            issues.append((repo_name, _read_issue(expected_file)))

    return issues


def _read_issue(issue_path: pathlib.Path) -> plug.Issue:
    with open(str(issue_path), "r", encoding=sys.getdefaultencoding()) as file:
        return plug.Issue(file.readline().strip(), file.read())


def _parse_multi_issues_file(
    issues_file: pathlib.Path,
) -> Iterable[Tuple[str, plug.Issue]]:
    with open(
        str(issues_file), mode="r", encoding=sys.getdefaultencoding()
    ) as file:
        lines = list(file.readlines())

    if not lines or not re.match(BEGIN_ISSUE_PATTERN, lines[0], re.IGNORECASE):
        raise plug.PlugError(
            "first line of multi issues file not #ISSUE# line"
        )

    issue_blocks = _extract_issue_blocks(lines)
    return list(_extract_issues(issue_blocks, lines))


def _extract_issue_blocks(lines: List[str]):
    issue_blocks = []
    prev = 0
    for i, line in enumerate(lines[1:], 1):
        if re.match(BEGIN_ISSUE_PATTERN, line, re.IGNORECASE):
            issue_blocks.append((prev, i))
            prev = i
    issue_blocks.append((prev, len(lines)))
    return issue_blocks


def _extract_issues(issue_blocks: Tuple[int, int], lines: List[str]):
    for begin, end in issue_blocks:
        repo_name, title = re.match(
            BEGIN_ISSUE_PATTERN, lines[begin], re.IGNORECASE
        ).groups()
        body = "".join(lines[begin + 1 : end])
        yield (repo_name, plug.Issue(title=title.strip(), body=body.rstrip()))
