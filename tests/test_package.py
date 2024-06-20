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
from unittest import TestCase
from unittest import mock

import pytest
from packageurl import PackageURL

from fetchcode.package import get_cocoapods_data_from_purl
from fetchcode.package import info
from fetchcode.package_util import construct_cocoapods_package
from fetchcode.package_util import get_cocoapod_tags

# Set to True to regenerate expected JSON files.
REGEN = False


def load_json(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


def check_packages(packages, expected_file, regen=REGEN):
    packages = [p.to_dict() for p in packages]
    if regen:
        with open(expected_file, "w") as f:
            json.dump(packages, f, indent=2)
        expected_packages = packages
    else:
        expected_packages = load_json(expected_file)

    assert packages == expected_packages


@mock.patch("fetchcode.package.get_response")
def test_cargo_packages(mock_get):
    side_effect = [load_json("tests/data/cargo_mock_data.json")]
    purl = "pkg:cargo/rand"
    expected_data = "tests/data/cargo.json"
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_npm_packages(mock_get):
    side_effect = [load_json("tests/data/npm_mock_data.json")]
    purl = "pkg:npm/express"
    expected_data = "tests/data/npm.json"
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_pypi_packages(mock_get):
    side_effect = [load_json("tests/data/pypi_mock_data.json")]
    purl = "pkg:pypi/flask"
    expected_data = "tests/data/pypi.json"
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_bitbucket_packages(mock_get):
    side_effect = [
        load_json("tests/data/bitbucket_mock_data.json"),
        load_json("tests/data/bitbucket_mock_release_data.json"),
    ]
    purl = "pkg:bitbucket/litmis/python-itoolkit"
    expected_data = "tests/data/bitbucket.json"
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_rubygems_packages(mock_get):
    side_effect = [load_json("tests/data/rubygems_mock_data.json")]
    purl = "pkg:rubygems/rubocop"
    expected_data = "tests/data/rubygems.json"
    mock_get.side_effect = side_effect
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package.get_response")
def test_tuby_package_with_invalid_url(mock_get):
    with pytest.raises(Exception) as e_info:
        purl = "pkg:ruby/file"
        packages = list(info(purl))
        assert "Failed to fetch: https://rubygems.org/api/v1/gems/file.json" == e_info


@mock.patch("fetchcode.package_util.utils.make_head_request")
@mock.patch("fetchcode.package_util.utils.get_github_rest")
@mock.patch("fetchcode.package_util.utils.get_response")
@mock.patch("fetchcode.package.get_cocoapod_tags")
@mock.patch("fetchcode.package.get_hashed_path")
def test_cocoapods_packages(
    mock_get_hashed_path,
    mock_get_cocoapod_tags,
    mock_get_response,
    mock_get_github_rest,
    mock_make_head_request,
):
    mock_get_hashed_path.return_value = "5/5/b"

    mock_get_cocoapod_tags.return_value = [
        '0.1.5',
        '0.1.4',
        '0.1.3',
        '0.1.2',
        '0.1.1',
        '0.1.0',
    ]

    mock_get_response.side_effect = file_json("tests/data/cocoapods/mock_get_response_side_effect.json")

    mock_get_github_rest.return_value = load_json("tests/data/cocoapods/mock_get_github_rest_return_value.json")

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_make_head_request.return_value = mock_response

    purl = "pkg:cocoapods/ASNetworking"
    expected_data = "tests/data/cocoapods.json"
    packages = list(info(purl))
    check_packages(packages, expected_data)


@mock.patch("fetchcode.package_util.utils.make_head_request")
@mock.patch("fetchcode.package_util.utils.get_github_rest")
@mock.patch("fetchcode.package_util.utils.get_response")
@mock.patch("fetchcode.package.get_cocoapod_tags")
@mock.patch("fetchcode.package.get_hashed_path")
def test_get_cocoapods_data_from_purl(
    mock_get_hashed_path,
    mock_get_cocoapod_tags,
    mock_get_response,
    mock_get_github_rest,
    mock_make_head_request,
):
    """
    This already-existing test is structurally identical to the new
    test_cocoapods_packages() except this test checks the
    get_cocoapods_data_from_purl() function rather than list(info(purl)).
    """
    mock_get_hashed_path.return_value = "5/5/b"

    mock_get_cocoapod_tags.return_value = [
        '0.1.5',
        '0.1.4',
        '0.1.3',
        '0.1.2',
        '0.1.1',
        '0.1.0',
    ]

    mock_get_response.side_effect = file_json("tests/data/cocoapods/mock_get_response_side_effect.json")

    mock_get_github_rest.return_value = load_json("tests/data/cocoapods/mock_get_github_rest_return_value.json")

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_make_head_request.return_value = mock_response

    expected_result_to_dict = file_json("tests/data/cocoapods/expected_result_to_dict.json")
    purl = "pkg:cocoapods/ASNetworking"
    actual_result = get_cocoapods_data_from_purl(purl)

    for pkg, expected_pkg_to_dict in zip(list(actual_result), expected_result_to_dict):
        pkg_to_json = json.dumps(pkg.to_dict())
        expected_pkg_to_dict_json_dumps = json.dumps(expected_pkg_to_dict)
        assert pkg_to_json == expected_pkg_to_dict_json_dumps


@mock.patch("fetchcode.package_util.utils.get_text_response")
def test_get_cocoapod_tags(mock_get):
    side_effect = [file_content("tests/data/cocoapods/cocoapod_all_pods_versions_5_1_f.txt")]
    mock_get.side_effect = side_effect
    cocoapods_org_pod_name = "DeptFlow"
    api = "https://cdn.cocoapods.org"
    hashed_path = "5/1/f"
    hashed_path_underscore = hashed_path.replace("/", "_")
    file_prefix = "all_pods_versions_"
    spec = f"{api}/{file_prefix}{hashed_path_underscore}.txt"
    expected_tags = ['0.1.0', '0.1.1', '0.2.0', '0.3.0']
    tags = get_cocoapod_tags(spec, cocoapods_org_pod_name)
    tags = sorted(tags)
    assert tags == expected_tags


@mock.patch("fetchcode.package_util.utils.get_response")
@mock.patch("fetchcode.package_util.utils.make_head_request")
@mock.patch("fetchcode.package_util.utils.get_github_rest")
def test_construct_cocoapods_package(mock_get_github_rest, mock_make_head_request, mock_get_response):
    mock_get_github_rest.return_value = "Failed to fetch: https://api.github.com/repos/KevalPatel94/KVLLibraries"

    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_make_head_request.return_value = mock_response

    mock_get_response.return_value = load_json("tests/data/cocoapods/get_response_kvllibraries.json")

    expected_construct_cocoapods_package = load_json("tests/data/cocoapods/expected_construct_cocoapods_package.json")

    purl = PackageURL.from_string("pkg:cocoapods/KVLLibraries")
    name = "KVLLibraries"
    hashed_path = "5/1/f"
    repository_homepage_url = "https://cocoapods.org/pods/KVLLibraries"
    gh_repo_owner = "KevalPatel94"
    gh_repo_name = "KVLLibraries"
    tag = "1.1.0"

    actual_output = construct_cocoapods_package(purl, name, hashed_path, repository_homepage_url, gh_repo_owner, gh_repo_name, tag)
    actual = json.dumps(actual_output.to_dict())
    expected = json.dumps(expected_construct_cocoapods_package)
    assert actual == expected


class GitHubSourceTestCase(TestCase):
    def check_result(self, filename, packages, regen=False):
        result = [p.to_dict() for p in packages]

        if regen:
            with open(filename, "w") as file:
                json.dump(result, file, indent=4)

        with open(filename) as file:
            expected = json.load(file)

        result = json.loads(json.dumps(result))

        self.assertListEqual(expected, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_avahi(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/avahi/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/avahi/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/avahi-expected.json"
        result = info("pkg:github/avahi/avahi")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_avahi(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/avahi/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/avahi/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/avahi-expected.json"
        result = info("pkg:github/avahi/avahi")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_bpftool(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/bpftool/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/bpftool/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/bpftool-expected.json"
        result = info("pkg:github/libbpf/bpftool")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_brotli(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/brotli/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/brotli/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/brotli-expected.json"
        result = info("pkg:github/google/brotli")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_dosfstools(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/dosfstools/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/dosfstools/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/dosfstools-expected.json"
        result = info("pkg:github/dosfstools/dosfstools")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_genext2fs(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/genext2fs/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/genext2fs/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/genext2fs-expected.json"
        result = info("pkg:github/bestouff/genext2fs")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_inotify_tools(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/inotify-tools/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/inotify-tools/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/inotify-tools-expected.json"
        result = info("pkg:github/inotify-tools/inotify-tools")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_llvm_project(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/llvm-project/github_mock_data_1.json",
            "tests/data/package/github/llvm-project/github_mock_data_2.json",
            "tests/data/package/github/llvm-project/github_mock_data_3.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/llvm-project/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/llvm-project-expected.json"
        result = info("pkg:github/llvm/llvm-project")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_miniupnpc(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/miniupnp/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/miniupnp/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/miniupnpc-expected.json"
        result = info("pkg:generic/miniupnpc")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_miniupnpd(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/miniupnp/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/miniupnp/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/miniupnpd-expected.json"
        result = info("pkg:generic/miniupnpd")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_minissdpd(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/miniupnp/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/miniupnp/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/minissdpd-expected.json"
        result = info("pkg:generic/minissdpd")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_nix(self, mock_github_response, mock_get_response):
        test_data = [
            "tests/data/package/github/nix/github_mock_data_1.json",
            "tests/data/package/github/nix/github_mock_data_2.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/nix/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/nix-expected.json"
        result = info("pkg:github/nixos/nix")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_pupnp(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/pupnp/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/pupnp/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/pupnp-expected.json"
        result = info("pkg:github/pupnp/pupnp")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_cpython(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/cpython/github_mock_data_1.json",
            "tests/data/package/github/cpython/github_mock_data_2.json",
            "tests/data/package/github/cpython/github_mock_data_3.json",
            "tests/data/package/github/cpython/github_mock_data_4.json",
            "tests/data/package/github/cpython/github_mock_data_5.json",
            "tests/data/package/github/cpython/github_mock_data_6.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/cpython/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/cpython-expected.json"
        result = info("pkg:github/python/cpython")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_rpm(self, mock_github_response, mock_get_response):
        test_data = [
            "tests/data/package/github/rpm/github_mock_data_1.json",
            "tests/data/package/github/rpm/github_mock_data_2.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/rpm/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/rpm-expected.json"
        result = info("pkg:github/rpm-software-management/rpm")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_shadow(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/shadow/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/shadow/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/shadow-expected.json"
        result = info("pkg:github/shadow-maint/shadow")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_sqlite(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/sqlite/github_mock_data_1.json",
            "tests/data/package/github/sqlite/github_mock_data_2.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/sqlite/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/sqlite-expected.json"
        result = info("pkg:github/sqlite/sqlite")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_squashfs_tools(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/squashfs-tools/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/squashfs-tools/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/squashfs-tools-expected.json"
        result = info("pkg:github/plougher/squashfs-tools")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_wireless_tools(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/wireless-tools/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/wireless-tools/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/wireless-tools-expected.json"
        result = info("pkg:github/hewlettpackard/wireless-tools")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_uboot(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/u-boot/github_mock_data_1.json",
            "tests/data/package/github/u-boot/github_mock_data_2.json",
            "tests/data/package/github/u-boot/github_mock_data_3.json",
            "tests/data/package/github/u-boot/github_mock_data_4.json",
            "tests/data/package/github/u-boot/github_mock_data_5.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/u-boot/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/u-boot-expected.json"
        result = info("pkg:github/u-boot/u-boot")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_erofs_utils(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/erofs-utils/github_mock_data_1.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/erofs-utils/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/erofs-utils-expected.json"
        result = info("pkg:generic/erofs-utils")

        self.check_result(expected_file, result)

    @mock.patch("fetchcode.utils.get_response")
    @mock.patch("fetchcode.utils.github_response")
    def test_packages_github_source_openssl(
        self, mock_github_response, mock_get_response
    ):
        test_data = [
            "tests/data/package/github/openssl/github_mock_data_1.json",
            "tests/data/package/github/openssl/github_mock_data_2.json",
            "tests/data/package/github/openssl/github_mock_data_3.json",
            "tests/data/package/github/openssl/github_mock_data_4.json",
        ]
        mock_github_response.side_effect = [file_json(file) for file in test_data]
        mock_get_response.return_value = file_json(
            "tests/data/package/github/openssl/github_mock_data_0.json"
        )

        expected_file = "tests/data/package/github/openssl-expected.json"
        result = info("pkg:openssl/openssl")

        self.check_result(expected_file, result)


class DirListedTestCase(TestCase):
    def check_result(self, filename, packages, regen=False):
        result = [p.to_dict() for p in packages]

        if regen:
            with open(filename, "w") as file:
                json.dump(result, file, indent=4)

        with open(filename) as file:
            expected = json.load(file)

        result = json.loads(json.dumps(result))

        self.assertListEqual(expected, result)

    @mock.patch("requests.get")
    def test_packages_openssh(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/openssh/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/openssh-expected.json"
        result = info("pkg:generic/openssh")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_syslinux(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/syslinux/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/syslinux-expected.json"
        result = info("pkg:generic/syslinux")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_toybox(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/toybox/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/toybox-expected.json"
        result = info("pkg:generic/toybox")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_uclibc(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/uclibc/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/uclibc-expected.json"
        result = info("pkg:generic/uclibc")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_uclibc_ng(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/uclibc-ng/index.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/0.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/1.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/2.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/3.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/4.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/5.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/6.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/7.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/8.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/9.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/10.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/11.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/12.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/13.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/14.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/15.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/16.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/17.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/18.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/19.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/20.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/21.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/22.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/23.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/24.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/25.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/26.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/27.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/28.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/29.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/30.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/31.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/32.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/33.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/34.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/35.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/36.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/37.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/38.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/39.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/40.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/41.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/42.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/43.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/44.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/45.html",
            "tests/data/package/dirlisting/generic/uclibc-ng/46.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/uclibc-ng-expected.json"
        result = info("pkg:generic/uclibc-ng")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_wpa_supplicant(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/wpa_supplicant/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = (
            "tests/data/package/dirlisting/generic/wpa_supplicant-expected.json"
        )
        result = info("pkg:generic/wpa_supplicant")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_gnu_glibc(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/gnu/glibc/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/gnu/glibc-expected.json"
        result = info("pkg:gnu/glibc")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_util_linux(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/util-linux/index.html",
            "tests/data/package/dirlisting/generic/util-linux/0.html",
            "tests/data/package/dirlisting/generic/util-linux/1.html",
            "tests/data/package/dirlisting/generic/util-linux/2.html",
            "tests/data/package/dirlisting/generic/util-linux/3.html",
            "tests/data/package/dirlisting/generic/util-linux/4.html",
            "tests/data/package/dirlisting/generic/util-linux/5.html",
            "tests/data/package/dirlisting/generic/util-linux/6.html",
            "tests/data/package/dirlisting/generic/util-linux/7.html",
            "tests/data/package/dirlisting/generic/util-linux/8.html",
            "tests/data/package/dirlisting/generic/util-linux/9.html",
            "tests/data/package/dirlisting/generic/util-linux/10.html",
            "tests/data/package/dirlisting/generic/util-linux/11.html",
            "tests/data/package/dirlisting/generic/util-linux/12.html",
            "tests/data/package/dirlisting/generic/util-linux/13.html",
            "tests/data/package/dirlisting/generic/util-linux/14.html",
            "tests/data/package/dirlisting/generic/util-linux/15.html",
            "tests/data/package/dirlisting/generic/util-linux/16.html",
            "tests/data/package/dirlisting/generic/util-linux/17.html",
            "tests/data/package/dirlisting/generic/util-linux/18.html",
            "tests/data/package/dirlisting/generic/util-linux/19.html",
            "tests/data/package/dirlisting/generic/util-linux/20.html",
            "tests/data/package/dirlisting/generic/util-linux/21.html",
            "tests/data/package/dirlisting/generic/util-linux/22.html",
            "tests/data/package/dirlisting/generic/util-linux/23.html",
            "tests/data/package/dirlisting/generic/util-linux/24.html",
            "tests/data/package/dirlisting/generic/util-linux/25.html",
            "tests/data/package/dirlisting/generic/util-linux/26.html",
            "tests/data/package/dirlisting/generic/util-linux/27.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/util-linux-expected.json"
        result = info("pkg:generic/util-linux")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_busybox(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/busybox/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/busybox-expected.json"
        result = info("pkg:generic/busybox")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_bzip2(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/bzip2/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/bzip2-expected.json"
        result = info("pkg:generic/bzip2")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_dnsmasq(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/dnsmasq/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/dnsmasq-expected.json"
        result = info("pkg:generic/dnsmasq")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_dropbear(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/dropbear/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/dropbear-expected.json"
        result = info("pkg:generic/dropbear")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_ebtables(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/ebtables/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/ebtables-expected.json"
        result = info("pkg:generic/ebtables")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_hostapd(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/hostapd/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/hostapd-expected.json"
        result = info("pkg:generic/hostapd")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_iproute2(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/iproute2/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/iproute2-expected.json"
        result = info("pkg:generic/iproute2")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_iptables(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/iptables/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/iptables-expected.json"
        result = info("pkg:generic/iptables")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_libnl(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/libnl/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/libnl-expected.json"
        result = info("pkg:generic/libnl")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_lighttpd(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/lighttpd/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/lighttpd-expected.json"
        result = info("pkg:generic/lighttpd")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_nftables(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/nftables/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/nftables-expected.json"
        result = info("pkg:generic/nftables")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_samba(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/samba/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/samba-expected.json"
        result = info("pkg:generic/samba")

        self.check_result(expected_file, result)

    def test_packages_ipkg(self):
        expected_file = "tests/data/package/dirlisting/generic/ipkg-expected.json"
        result = info("pkg:generic/ipkg")

        self.check_result(expected_file, result)

    def test_packages_udhcp(self):
        expected_file = "tests/data/package/dirlisting/generic/udhcp-expected.json"
        result = info("pkg:generic/udhcp")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_linux(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/linux/index.html",
            "tests/data/package/dirlisting/generic/linux/0.html",
            "tests/data/package/dirlisting/generic/linux/1.html",
            "tests/data/package/dirlisting/generic/linux/2.html",
            "tests/data/package/dirlisting/generic/linux/3.html",
            "tests/data/package/dirlisting/generic/linux/4.html",
            "tests/data/package/dirlisting/generic/linux/5.html",
            "tests/data/package/dirlisting/generic/linux/6.html",
            "tests/data/package/dirlisting/generic/linux/7.html",
            "tests/data/package/dirlisting/generic/linux/8.html",
            "tests/data/package/dirlisting/generic/linux/9.html",
            "tests/data/package/dirlisting/generic/linux/10.html",
            "tests/data/package/dirlisting/generic/linux/11.html",
            "tests/data/package/dirlisting/generic/linux/12.html",
            "tests/data/package/dirlisting/generic/linux/13.html",
            "tests/data/package/dirlisting/generic/linux/14.html",
            "tests/data/package/dirlisting/generic/linux/15.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/linux-expected.json"
        result = info("pkg:generic/linux")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_mtd_utils(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/mtd-utils/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/mtd-utils-expected.json"
        result = info("pkg:generic/mtd-utils")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_barebox(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/barebox/index.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/barebox-expected.json"
        result = info("pkg:generic/barebox")

        self.check_result(expected_file, result)

    @mock.patch("requests.get")
    def test_packages_e2fsprogs(self, mock_get):
        test_data = [
            "tests/data/package/dirlisting/generic/e2fsprogs/index.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/0.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/1.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/2.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/3.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/4.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/5.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/6.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/7.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/8.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/9.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/10.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/11.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/12.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/13.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/14.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/15.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/16.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/17.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/18.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/19.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/20.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/21.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/22.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/23.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/24.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/25.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/26.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/27.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/28.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/29.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/30.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/31.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/32.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/33.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/34.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/35.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/36.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/37.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/38.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/39.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/40.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/41.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/42.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/43.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/44.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/45.html",
            "tests/data/package/dirlisting/generic/e2fsprogs/46.html",
        ]

        mock_get.side_effect = [
            type(
                "Response",
                (),
                {
                    "content": file_content(file).encode(),
                    "raise_for_status": lambda: None,
                },
            )
            for file in test_data
        ]

        expected_file = "tests/data/package/dirlisting/generic/e2fsprogs-expected.json"
        result = info("pkg:generic/e2fsprogs")

        self.check_result(expected_file, result)


def file_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def file_content(file_name):
    with open(file_name) as file:
        return file.read()
