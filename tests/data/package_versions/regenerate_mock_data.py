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

import yaml

from fetchcode.package_versions import get_response

test_sources = [
    {
        "ecosystem": "cargo",
        "purl": "pkg:cargo/yprox",
        "source": "https://crates.io/api/v1/crates/yprox",
        "headers": {"User-Agent": "fc"},
        "content_type": "json",
        "file-name": "cargo_mock_data.json",
    },
    {
        "ecosystem": "composer",
        "purl": "pkg:composer/laravel/laravel",
        "source": "https://repo.packagist.org/p/laravel/laravel.json",
        "content_type": "json",
        "file-name": "composer_mock_data.json",
    },
    {
        "ecosystem": "conan",
        "purl": "pkg:conan/openssl",
        "source": "https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/openssl/config.yml",
        "content_type": "yaml",
        "file-name": "conan_mock_data.yml",
    },
    {
        "ecosystem": "deb",
        "purl": "pkg:deb/debian/attr",
        "source": "https://sources.debian.org/api/src/attr",
        "headers": {"Connection": "keep-alive"},
        "content_type": "json",
        "file-name": "deb_mock_data.json",
    },
    {
        "ecosystem": "gem",
        "purl": "pkg:gem/ruby-advisory-db-check",
        "source": "https://rubygems.org/api/v1/versions/ruby-advisory-db-check.json",
        "content_type": "json",
        "file-name": "gem_mock_data.json",
    },
    {
        "ecosystem": "hex",
        "purl": "pkg:hex/jason",
        "source": "https://hex.pm/api/packages/jason",
        "content_type": "json",
        "file-name": "hex_mock_data.json",
    },
    {
        "ecosystem": "launchpad",
        "purl": "pkg:deb/ubuntu/abcde",
        "source": "https://api.launchpad.net/1.0/ubuntu/+archive/primary?exact_match=true&source_name=abcde&ws.op=getPublishedSources&ws.size=75&memo=75&ws.start=75",
        "content_type": "json",
        "file-name": "launchpad_mock_data.json",
    },
    {
        "ecosystem": "maven",
        "purl": "pkg:maven/org.apache.xmlgraphics/batik-anim",
        "source": "https://repo1.maven.org/maven2/org/apache/xmlgraphics/batik-anim/maven-metadata.xml",
        "content_type": "binary",
        "file-name": "maven_mock_data.xml",
    },
    {
        "ecosystem": "npm",
        "purl": "pkg:npm/%40angular/animation",
        "source": "https://registry.npmjs.org/%40angular/animation",
        "content_type": "json",
        "file-name": "npm_mock_data.json",
    },
    {
        "ecosystem": "nuget",
        "purl": "pkg:nuget/EnterpriseLibrary.Common",
        "source": "https://api.nuget.org/v3/registration5-semver1/enterpriselibrary.common/index.json",
        "file-name": "nuget_mock_data.json",
    },
    {
        "ecosystem": "pypi",
        "purl": "pkg:pypi/django",
        "source": "https://pypi.org/pypi/django/json",
        "file-name": "pypi_mock_data.json",
    },
]


def fetch_mock_data():
    for source in test_sources:
        content_type = source.get("content_type", "json")
        response = get_response(
            url=source["source"],
            content_type=content_type,
            headers=source.get("headers", None),
        )
        mock_file = f'tests/data/package_versions/{source["file-name"]}'

        if content_type == "binary":
            with open(mock_file, "wb") as file:
                file.write(response)
        else:
            with open(mock_file, "w") as file:
                if content_type == "json":
                    json.dump(response, file, indent=4)
                elif content_type == "yaml":
                    yaml.dump(response, file)
                else:
                    file.write(response)

def fetch_golang_mock_data():
    url = f"https://proxy.golang.org/github.com/blockloop/scan/@v/list"
    version_list = get_response(url=url, content_type="text")
    for version in version_list.split():
        file_name = f"tests/data/package_versions/golang/versions/golang_mock_{version}_data.json"
        response = get_response(
            url=f"https://proxy.golang.org/github.com/blockloop/scan/@v/{version}.info",
            content_type="json",
        )
        with open(file_name, "w") as file:
            json.dump(response, file, indent=4)
    golang_version_list_file = (
        "tests/data/package_versions/golang/golang_mock_meta_data.txt"
    )
    with open(golang_version_list_file, "w") as file:
        file.write(version_list)

def main():
    fetch_mock_data()
    fetch_golang_mock_data()

if __name__ == "__main__":
    # Script to regenerate mock data for python_versions 
    main()