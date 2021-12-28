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
from textwrap import indent
from typing import Iterable, Tuple, List, Mapping

import repobee_plug as plug
from repobee_feedback._generate_multi_issues_file import (  # noqa: F401
    GenerateMultiIssuesFile,
)

PLUGIN_NAME = "feedback"

BEGIN_ISSUE_PATTERN = r"#ISSUE#(.*?)#(.*)"
INDENTATION_STR = "    "
TRUNC_SIGN = "[...]"


def callback(args: argparse.Namespace, api: plug.PlatformAPI) -> None:
    repo_name_to_team: Mapping[str, plug.StudentTeam] = {
        plug.generate_repo_name(
            student_team.name, assignment_name
        ): student_team
        for student_team in args.students
        for assignment_name in args.assignments
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
            repo = api.get_repo(repo_name, repo_name_to_team[repo_name].name)
            api.create_issue(issue.title, issue.body, repo)
        else:
            plug.echo("Skipping {}".format(repo_name))


class Feedback(plug.Plugin, plug.cli.Command):
    __settings__ = plug.cli.command_settings(
        help="open feedback issues in student repos",
        description="Collect issues from issue files "
        "to create issues in students repos. Alternatively, all issues can "
        "written in a single multi-issues file. See "
        "https://github.com/repobee/repobee-feedback for detailed information"
        "on the format of the issue files.",
        category=plug.cli.CoreCommand.issues,
        action="feedback",
        base_parsers=[plug.BaseParser.ASSIGNMENTS, plug.BaseParser.STUDENTS],
    )

    allow_missing = plug.cli.flag(
        help="emit a warning (instead of crashing) on missing issues"
    )
    batch_mode = plug.cli.flag(
        short_name="-b", help="run without any yes/no prompts"
    )
    truncation_length = plug.cli.option(
        short_name="--tl",
        help=(
            "in interactive mode, truncates the body of an issue to this "
            "many characters"
        ),
        converter=int,
        default=sys.maxsize,
    )

    group_mutex = plug.cli.mutually_exclusive_group(
        issues_dir=plug.cli.option(
            short_name="--id",
            help=(
                "directory containing issue files "
                "named <STUDENT_REPO_NAME>.md, in which the first line is "
                "assumed to be the title"
            ),
            converter=pathlib.Path,
            default=".",
        ),
        multi_issues_file=plug.cli.option(
            short_name="--mi",
            help=(
                "file containing issues to be opened, where each separate "
                "issue starts with the line "
                "#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>, followed by its "
                "body"
            ),
            converter=pathlib.Path,
        ),
        __required__=True,
    )

    def command(self, api: plug.PlatformAPI):
        callback(self.args, api)


def _indent_issue_body(body: str, trunc_len: int):
    indented_body = indent(body[:trunc_len], INDENTATION_STR)
    body_end = TRUNC_SIGN if len(body) > trunc_len else ""
    return indented_body + body_end


def _ask_for_open(issue: plug.Issue, repo_name: str, trunc_len: int) -> bool:
    indented_body = _indent_issue_body(issue.body, trunc_len)
    issue_description = (
        f'\nProcessing issue "{issue.title}" for {repo_name}:\n{indented_body}'
    )
    plug.echo(issue_description)
    return (
        input(f'Open issue "{issue.title}" in repo {repo_name}? (y/n) ') == "y"
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
            plug.log.warning(msg)
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


def _extract_issues(issue_blocks: Iterable[Tuple[int, int]], lines: List[str]):
    for begin, end in issue_blocks:
        match = re.match(BEGIN_ISSUE_PATTERN, lines[begin], re.IGNORECASE)
        assert match

        repo_name, title = match.groups()
        body = "".join(lines[begin + 1 : end])
        yield (repo_name, plug.Issue(title=title.strip(), body=body.rstrip()))
