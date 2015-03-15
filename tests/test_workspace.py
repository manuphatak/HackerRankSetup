# coding=utf-8
import difflib
import tempfile
import unittest
import json
import cPickle
import shutil
import os.path

import mock
import nose.tools as test

from hackerranksetup import Challenge, Readme


root_directory = os.path.realpath(os.path.expanduser('~/code/HackerRankSetup'))
expected_assets = lambda x: os.path.realpath(
    os.path.join(root_directory, 'tests/test_assets', x))


class TestWorkspace(unittest.TestCase):
    with open(expected_assets('hackerrank_response.p'), 'rb') as response:
        hackerrank_response = cPickle.load(response)
    with open(expected_assets('mock_tex_response.json')) as response:
        tex_response = json.load(response)
    test_url = ('https://www.hackerrank.com/'
                'challenges/sherlock-and-queries')
    _temp_dir = None

    @classmethod
    def setUpClass(cls):
        tempfile.tempdir = os.path.realpath(
            os.path.join(root_directory, 'tests/.tmp'))
        cls._temp_dir = tempfile.mkdtemp()
        cls.assets = os.path.realpath(os.path.join(root_directory, 'assets'))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls._temp_dir):
            shutil.rmtree(cls._temp_dir)

    def setUp(self):
        self.challenge = Challenge.Challenge(self.test_url)
        self.readme = Readme.Readme(self.challenge, destination=self._temp_dir,
                                    assets=self.assets)

        th_patcher = mock.patch('hackerranksetup.Readme.TexImage')
        self.MockTexHandler = th_patcher.start()
        self.addCleanup(th_patcher.stop)
        test_tex = self.MockTexHandler.return_value
        test_tex.get.side_effect = self.tex_response.get
        assert Readme.TexImage is self.MockTexHandler

        rq_patcher = mock.patch('hackerranksetup.Challenge.requests')
        self.addCleanup(rq_patcher.stop)
        self.MockRequests = rq_patcher.start()
        self.MockRequests.get.return_value = self.hackerrank_response
        assert Challenge.requests is self.MockRequests

    def tearDown(self):
        del self.readme

    def test_class_initializes_properly(self):
        test.assert_equals(os.path.realpath(self.readme.destination),
                           os.path.realpath(self._temp_dir))
        test.assert_equals(self.challenge.url, self.test_url)
        rest_endpoint = ('https://www.hackerrank.com/'
                         'rest/contests/master/challenges/sherlock-and-queries')
        test.assert_equals(self.challenge.rest_endpoint, rest_endpoint)
        test.assert_is_none(self.challenge._model)
        test.assert_is_none(self.readme._source)
        test.assert_is_none(self.readme._readme)

    def test_build_source(self):
        source_file = expected_assets('sherlock-and-queries.md')
        with open(source_file) as source_file:
            source = self.readme.source
            expected = source_file.read()
            test.assert_equals(source, expected, self.diff(source, expected))

    def test_build_readme(self):
        with open(expected_assets('README.md')) as readme_file:
            readme = self.readme.readme
            expected = readme_file.read()
            test.assert_equals(readme, expected, self.diff(readme, expected))

    def test_run_creates_readme(self):
        test_source = expected_assets('sherlock-and-queries.md')
        with open(test_source) as test_source:
            self.readme._source = test_source.read()
        self.readme.save()
        expected_readme = expected_assets('README.md')
        actual_readme = os.path.join(self._temp_dir, 'README.md')

        with open(expected_readme) as expected_readme, open(
                actual_readme) as actual_readme:
            expected = expected_readme.read()
            actual = actual_readme.read()
            test.assert_equals(expected, actual, self.diff(actual, expected))

    def test_throw_error_invalid_url(self):
        bad_url = 'asdfasdf'
        self.challenge.url = bad_url

        def get_rest_endpoint_error_test():
            return self.challenge.rest_endpoint

        test.assert_raises(ValueError, get_rest_endpoint_error_test)

    @staticmethod
    def diff(actual, expected):
        actual, expected = actual.splitlines(), expected.splitlines()
        summary = '\n'.join(difflib.unified_diff(expected, actual))
        full = '\n'.join(difflib.Differ().compare(expected, actual))
        return '\n{}\n\n{}'.format(summary, full)


if __name__ == '__main__':
    unittest.main()
