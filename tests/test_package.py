# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.

# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org

# This software is licensed under the Apache License version 2.0.

# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from unittest import mock

from fetchcode.package import info


def file_data(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


def match_data(packages, expected_data):
    data = [dict(p.to_dict()) for p in packages]
    expected_data_dict = dict(expected_data)
    expected_data = [dict(expected_data_dict[p]) for p in expected_data_dict]
    assert expected_data == data


@mock.patch("fetchcode.package.get_response")
def test_cargo_packages(mock_get):
    side_effect = [file_data("tests/data/cargo_mock_data.json")]
    purl = "pkg:cargo/rand"
    expected_data = file_data("tests/data/cargo.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_npm_packages(mock_get):
    side_effect = [file_data("tests/data/npm_mock_data.json")]
    purl = "pkg:npm/express"
    expected_data = file_data("tests/data/npm.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_pypi_packages(mock_get):
    side_effect = [file_data("tests/data/pypi_mock_data.json")]
    purl = "pkg:pypi/flask"
    expected_data = file_data("tests/data/pypi.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_github_packages(mock_get):
    side_effect = [
        file_data("tests/data/github_mock_data.json"),
        file_data("tests/data/github_mock_release_data.json"),
    ]
    purl = "pkg:github/TG1999/fetchcode"
    expected_data = file_data("tests/data/github.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_bitbucket_packages(mock_get):
    side_effect = [
        file_data("tests/data/bitbucket_mock_data.json"),
        file_data("tests/data/bitbucket_mock_release_data.json"),
    ]
    purl = "pkg:bitbucket/litmis/python-itoolkit"
    expected_data = file_data("tests/data/bitbucket.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_rubygems_packages(mock_get):
    side_effect = [file_data("tests/data/rubygems_mock_data.json")]
    purl = "pkg:rubygems/rubocop"
    expected_data = file_data("tests/data/rubygems.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_homebrew_packages(mock_get):
    side_effect = [file_data("tests/data/homebrew_mock_data1.json")]
    purl = "pkg:homebrew/node"
    expected_data = file_data("tests/data/homebrew1.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)
    side_effect = [file_data("tests/data/homebrew_mock_data2.json")]
    purl = "pkg:homebrew/wget@1.21.1"
    expected_data = file_data("tests/data/homebrew2.json")
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    match_data(packages, expected_data)
