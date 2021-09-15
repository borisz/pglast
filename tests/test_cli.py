# -*- coding: utf-8 -*-
# :Project:   pglast -- Test the __main__.py module
# :Created:   lun 07 ago 2017 12:50:37 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017, 2018, 2019, 2021 Lele Gaifax
#

from contextlib import _RedirectStream, redirect_stdout
from io import StringIO
from os import unlink
from tempfile import NamedTemporaryFile

import pytest

from pglast.__main__ import main


class redirect_stdin(_RedirectStream):
    _stream = "stdin"


class UnclosableStream(StringIO):
    def close(self):
        pass


def test_cli_workhorse():
    with StringIO() as output:
        with redirect_stdout(output):
            with pytest.raises(SystemExit) as status:
                main(['-h'])
            assert status.value.args[0] == 0
        assert 'usage:' in output.getvalue()

    with StringIO("Select foo,bar Fron sometable") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                with pytest.raises(SystemExit) as status:
                    main([])
                assert str(status.value.args[0]) == \
                    'syntax error at or near "sometable", at index 20'

    with StringIO("Select foo,bar From sometable Where foo<>0") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main([])
            assert output.getvalue() == """\
SELECT foo
     , bar
FROM sometable
WHERE foo <> 0
"""

    output = NamedTemporaryFile(delete=False)
    try:
        main(['-S', "select 1", '-', output.name])
        with open(output.name) as f:
            assert f.read() == "SELECT 1\n"
    finally:
        unlink(output.name)

    with StringIO("Select 1") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--parse-tree'])
            assert "'val': {'@': 'Integer', 'val': 1}" in output.getvalue()

    with StringIO("Select 1") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main([])
            assert output.getvalue() == "SELECT 1\n"

    with StringIO("Select 1;") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main([])
            assert output.getvalue() == "SELECT 1\n"

    with StringIO("Select 1; Select 2") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main([])
            assert output.getvalue() == "SELECT 1;\n\nSELECT 2\n"

    with StringIO("Select 1; Select 2") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--semicolon-after-last-statement'])
            assert output.getvalue() == "SELECT 1;\n\nSELECT 2;\n"

    with StringIO("Select 'abcdef'") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--split-string-literals', '0'])
            assert output.getvalue() == "SELECT 'abcdef'\n"

    with StringIO("Select 'abcdef'") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--split-string-literals', '3'])
            assert output.getvalue() == """\
SELECT 'abc'
       'def'
"""

    with StringIO("Select /* one */ 1") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--preserve-comments'])
            assert output.getvalue() == "SELECT /* one */ 1\n"

    with StringIO("""\
select substring('abcd' from 1 for 2),
       substring('abcd' from 2),
       position('bc' in 'abcd'),
       trim(both '  abc  '),
       trim(both '*' from '***abc***'),
       trim(leading '*' from '***abc***'),
       trim(trailing '*' from '***abc***'),
       overlay('Txxxxas' placing 'hom' FROM 2 for 4)
""") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--special-functions', '--compact-lists-margin', '100'])
            assert output.getvalue() == """\
SELECT substring('abcd' FROM 1 FOR 2)
     , substring('abcd' FROM 2)
     , position('bc' IN 'abcd')
     , trim(BOTH FROM '  abc  ')
     , trim(BOTH '*' FROM '***abc***')
     , trim(LEADING '*' FROM '***abc***')
     , trim(TRAILING '*' FROM '***abc***')
     , overlay('Txxxxas' PLACING 'hom' FROM 2 FOR 4)
"""

    with StringIO("select extract(hour from t1.modtime), count(*) from t1") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--special-functions', '--compact-lists-margin', '120'])
            assert output.getvalue() == ("SELECT EXTRACT(HOUR FROM t1.modtime), count(*)\n"
                                         "FROM t1\n")

    with StringIO("select extract(hour from t1.modtime), count(*) from t1") as input:
        with UnclosableStream() as output:
            with redirect_stdin(input), redirect_stdout(output):
                main(['--special-functions', '--compact-lists-margin', '40'])
            assert output.getvalue() == ("SELECT EXTRACT(HOUR FROM t1.modtime)\n"
                                         "     , count(*)\n"
                                         "FROM t1\n")
