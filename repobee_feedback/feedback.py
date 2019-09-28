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


def callback(args: argparse.Namespace, api: plug.API) -> None:
    repo_names = plug.generate_repo_names(args.students, args.master_repo_names)
    if "multi_issues_file" in args and args.multi_issues_file is not None:
        issues_file = pathlib.Path(args.multi_issues_file).resolve()
        all_issues = _parse_multi_issues_file(issues_file)
    else:
        issues_dir = pathlib.Path(args.issues_dir).resolve()
        all_issues = _collect_issues(repo_names, issues_dir)
    issues = _extract_expected_issues(all_issues, repo_names)
    for repo_name, issue in issues:
        open_issue = args.batch_mode or _ask_for_open(
            issue, repo_name, args.truncation_length
        )
        if open_issue:
            api.open_issue(issue.title, issue.body, [repo_name])
        else:
            LOGGER.info("Skipping {}".format(repo_name))


class FeedbackCommand(plug.Plugin):
    def create_extension_command(self):
        parser = plug.ExtensionParser()
        parser.add_argument(
            "-b",
            "--batch-mode",
            help="Run without any yes/no promts.",
            action="store_true",
        )
        parser.add_argument(
            "--tl",
            "--truncation-length",
            help=(
                "In interactive mode, truncates the body of an issue at this "
                "many characters. If not specified, issue bodies are shown in "
                "full."
            ),
            dest="truncation_length",
            type=int,
            default=sys.maxsize,
        )
        issues_grp = parser.add_mutually_exclusive_group(required=True)
        issues_grp.add_argument(
            "--id",
            "--issues-dir",
            help=(
                "Directory containing issue files. The files should be "
                "named <STUDENT_REPO_NAME>.md (for example, "
                "slarse-task-1.md). The first line is assumed to be the "
                "title, and the rest the body. Defaults to the current "
                "directory."
            ),
            dest="issues_dir",
            type=str,
            default=".",
        )
        issues_grp.add_argument(
            "--mi",
            "--multi-issues-file",
            dest="multi_issues_file",
            help=(
                "File containing all issues to be openend. Each separate "
                "issue should begin with a line containing only "
                "#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>. For example, for "
                "student `slarse` and assignment `task-1` and issue title "
                "`Pass`, the line should read `#ISSUE#slarse-task-1#Pass` "
                "(without backticks). The very first line of the file must "
                "be an #ISSUE# line."
            ),
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="issue-feedback",
            help="Open issues in student repos based on local issue files.",
            description=(
                "Open issues in student repos based on local issue files. "
                "Operates in two different modes, depending on if you "
                "specify `--multi-issues-file` or `--issues-dir`. See the "
                "description of those options for details."
            ),
            callback=callback,
            requires_api=True,
            requires_base_parsers=[
                plug.BaseParser.REPO_NAMES,
                plug.BaseParser.STUDENTS,
            ],
        )


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
        input('Open issue "{}" in repo {}? (y/n) '.format(issue.title, repo_name))
        == "y"
    )


def _extract_expected_issues(
    repos_and_issues, repo_names
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
        raise plug.PlugError("Missing issues for: " + ", ".join(missing_repos))

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
    issues_file: pathlib.Path
) -> Iterable[Tuple[str, plug.Issue]]:
    with open(str(issues_file), mode="r", encoding=sys.getdefaultencoding()) as file:
        lines = list(file.readlines())

    if not lines or not re.match(BEGIN_ISSUE_PATTERN, lines[0], re.IGNORECASE):
        raise plug.PlugError("first line of multi issues file not #ISSUE# line")

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
