import sys

import repobee
from repobee_feedback._generate_multi_issues_file import (
    MULTI_ISSUES_FILENAME,
    GENERATE_MULTI_ISSUES_FILE_ACTION,
    GenerateMultiIssuesFile,
)


class TestGenerateMultiIssuesFile:
    """Tests generation of a multi-issues file"""

    def test_creates_non_empty_output_file(self, tmp_path):
        students = "alice bob".split()
        assignments = "task-1 task-2".split()
        command = [
            *GENERATE_MULTI_ISSUES_FILE_ACTION.as_name_tuple(),
            "--students",
            *students,
            "--assignments",
            *assignments,
        ]

        expected_content = (
            "#ISSUE#alice-task-1#<ISSUE-TITLE>\n"
            "<ISSUE-BODY>\n\n"
            "#ISSUE#bob-task-1#<ISSUE-TITLE>\n"
            "<ISSUE-BODY>\n\n"
            "#ISSUE#alice-task-2#<ISSUE-TITLE>\n"
            "<ISSUE-BODY>\n\n"
            "#ISSUE#bob-task-2#<ISSUE-TITLE>\n"
            "<ISSUE-BODY>"
        )

        repobee.run(
            command,
            plugins=[GenerateMultiIssuesFile],
            workdir=tmp_path,
        )

        outfile = tmp_path / MULTI_ISSUES_FILENAME
        content = outfile.read_text(encoding=sys.getdefaultencoding())
        assert outfile.is_file()
        assert content == expected_content
