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
        assignments = "task-1 task-2"
        command = [
            *GENERATE_MULTI_ISSUES_FILE_ACTION.as_name_tuple(),
            "--students",
            students,
            "--assignments",
            assignments,
        ]

        repobee.run(
            command,
            plugins=[GenerateMultiIssuesFile],
            workdir=tmp_path,
        )

        outfile = tmp_path / MULTI_ISSUES_FILENAME
        assert outfile.is_file()
        assert len(outfile.read_text(encoding=sys.getdefaultencoding())) > 0
