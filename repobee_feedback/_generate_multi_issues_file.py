"""A helper command to automatically generate a file called issue.md
wich contains templates of issues for multiple students assignments.

.. module:: _generate_multi_issues_file
    :synopsis: A helper command to automatically generate a file
    called issue.md wich contains templates of issues for multiple
    students assignments.

.. moduleauthor:: Marcelo Freitas
"""
import pathlib
import sys
from typing import List

import repobee_plug as plug
from repobee_plug.cli.categorization import Action

MULTI_ISSUES_FILENAME = "issue.md"

GENERATE_MULTI_ISSUES_FILE_ACTION = Action(
    name="generate-multi-issues-file",
    category=plug.cli.CoreCommand.issues,
)


class GenerateMultiIssuesFile(plug.Plugin, plug.cli.Command):
    __settings__ = plug.cli.command_settings(
        help=(
            "auto generate multi-issues file"
            " for the `issues feedback` command"
        ),
        description="Will generate a multi-issues file template "
        "where each pair of student assignment passed "
        "will become an issue that starts with the line "
        "#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>, followed by its "
        "body. Title and body should be filled appropriately later.",
        action=GENERATE_MULTI_ISSUES_FILE_ACTION,
        base_parsers=[plug.BaseParser.ASSIGNMENTS, plug.BaseParser.STUDENTS],
    )

    def command(self):
        content = _generate_multi_issues_file_content(
            self.args.students, self.args.assignments
        )

        pathlib.Path(MULTI_ISSUES_FILENAME).write_text(
            content, encoding=sys.getdefaultencoding()
        )

        plug.echo(f"Created multi-issues file '{MULTI_ISSUES_FILENAME}'")


def _generate_multi_issues_file_content(
    students: List[str], assignments: List[str]
) -> str:

    issue_headers = [
        f"#ISSUE#{repo_name}#<ISSUE-TITLE>\n<ISSUE-BODY>"
        for repo_name in plug.generate_repo_names(students, assignments)
    ]

    return "\n\n".join(issue_headers)
