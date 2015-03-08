# coding=utf-8
import urllib
import codecs
import os.path
import re

import requests

from HackerRankSetup.TexHandler import TexHandler


class HackerRankReadme(object):
    rest_base = (
        'https://www.hackerrank.com/rest/contests/master/challenges/')
    hackerrank_logo = (
        'https://www.hackerrank.com/assets/brand/typemark_60x200.png')

    def __init__(self, url, root='./', workspace='../workspace/',
                 assets='../assets/', readme_file_name='README.md'):
        self.root = os.path.realpath(root)
        self.assets = os.path.realpath(assets)
        self._workspace = os.path.realpath(workspace)

        self.url = url
        self.rest_endpoint = self.get_rest_endpoint(url)
        self.readme_file_name = readme_file_name
        self._source = None
        self._model = None
        self._readme = None
        self._source_file_name = None

    @property
    def directory(self):
        if not os.path.exists(self._workspace):
            os.makedirs(self._workspace)
        return self._workspace

    @property
    def source(self):
        self._source = self._source if self._source else self.build_source()
        return self._source

    @property
    def model(self):
        self._model = self._model if self._model else self.get_model()
        return self._model

    @property
    def readme(self):
        self._readme = self._readme if self._readme else self.build_readme()
        return self._readme

    def get_rest_endpoint(self, from_url):
        url_slug = re.search(r'/([a-z1-9-]+)/?$', from_url).group(1)
        return self.rest_base + url_slug

    @property
    def source_file_name(self):
        self._source_file_name = (
            self._source_file_name if self._source_file_name
            else '{}.md'.format(self.model['slug']))
        return self._source_file_name

    def run(self):
        with codecs.open(os.path.join(self.directory, self.source_file_name),
                         'w', encoding='utf8') as f:
            f.write(self.source)
        with codecs.open(os.path.join(self.directory, self.readme_file_name),
                         'w', encoding='utf8') as f:
            f.write(self.readme)
        return self

    def get_model(self):
        response = requests.get(self.rest_endpoint)
        return response.json()['model']

    def build_readme(self):
        tex_api = TexHandler()
        tex_api.assets = self.assets
        rel_assets = os.path.relpath(self.assets, self._workspace)
        footnote = {}

        def register_tex(match):
            match = match.group()
            tex_path = tex_api.get(match)
            match = match.replace('[', '').replace(']', '')
            footnote[match] = tex_path
            return '![{}]'.format(match)

        readme = self.source
        h3 = re.compile(ur'^\*\*([\w ?]+)\*\*$', re.M)
        readme = h3.sub(ur'###\1', readme)
        newline = (
            ur'(```)([^`]*?)(?(2)(```))'
            ur'|(?:(?:\n?(?: {4,})+.*\n)+\n?)'
            ur'|(?P<space>(?<!\n)\n(?!\n))')
        repl = lambda x: "\n\n" if x.group('space') else x.group()
        readme = re.compile(newline).sub(repl, readme)
        tex = re.compile(ur'\$[^$]+\$')
        readme = tex.sub(register_tex, readme)
        for k, v in footnote.iteritems():
            link = urllib.pathname2url(os.path.join(rel_assets, v))
            readme += '\n' + r'[{}]:{}'.format(k, link)
        return readme

    def build_source(self):
        model = self.model
        footnote = {'HackerRank': self.hackerrank_logo}
        logo = '![{0}]'.format('HackerRank')
        name = '#{}'.format(model['name'].strip())
        url_crumb = '{} \ {} \ {} \ {}'.format('HackerRank',
                                               model['track']['track_name'],
                                               model['track']['name'],
                                               model['name'])
        link = '[{}]({})'.format(url_crumb, self.url)
        preview = '{}'.format(model['preview'])
        body = (u'\n##{}\n{}'.format('Problem Statement', model['_data'][
            'problem_statement'].strip()))
        footnote = '\n[{}]:{}'.format('HackerRank', footnote['HackerRank'])

        source = u'\n'.join([logo, name, link, preview, body, footnote])

        source = re.compile(r' +$', re.M).sub('', source)
        source = re.compile(ur'\t', re.U).sub(u'    ', source)
        return source

    def __str__(self):
        return self.readme.encode('utf-8')


if __name__ == "__main__":
    _directory = '../proof_of_concept/'
    _assets = '../test_assets/'
    _url = raw_input('>>> ')
    print HackerRankReadme(_url, workspace=_directory, assets=_assets).run()