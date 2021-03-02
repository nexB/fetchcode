# fetchcode is a free software tool from nexB Inc. and others.
# Visit https://github.com/nexB/fetchcode for support and download.
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and http://aboutcode.org
#
# This software is licensed under the Apache License version 2.0.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at:
# http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from attr import attrs, attrib

from packageurl.contrib.route import NoRouteAvailable
from packageurl import PackageURL
from packageurl.contrib.route import Router
import requests

from fetchcode.packagedcode_models import Package

router = Router()


def info(url):
    """
    Return data according to the `url` string
    `url` string can be purl too
    """
    if url:
        try:
            return router.process(url)
        except NoRouteAvailable:
            return


def get_response(url):
    """
    Generate `Package` object for a `url` string
    """
    resp = requests.get(url)
    if "json" in dir(resp):
        return resp.json()

    raise Exception("Response of this URL does not contain json object")


def get_pypi_bugtracker_url(project_urls):
    bug_tracking_url = project_urls.get("Tracker")
    if not (bug_tracking_url):
        bug_tracking_url = project_urls.get("Issue Tracker")
    if not (bug_tracking_url):
        bug_tracking_url = project_urls.get("Bug Tracker")
    return bug_tracking_url


def get_pypi_codeview_url(project_urls):
    code_view_url = project_urls.get("Source")
    if not (code_view_url):
        code_view_url = project_urls.get("Code")
    if not (code_view_url):
        code_view_url = project_urls.get("Source Code")
    return code_view_url


@router.route("pkg:cargo/.*")
def get_cargo_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of cargo type
    """
    purl = PackageURL.from_string(purl)
    base_url = "https://crates.io"
    name = purl.name
    version = purl.version
    api_url = f"{base_url}/api/v1/crates/{name}"
    download_url = f"{api_url}/{version}/download" if version else None
    response = get_response(api_url)
    crate = response.get("crate") or {}
    homepage_url = crate.get("homepage")
    code_view_url = crate.get("repository")
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        code_view_url=code_view_url,
        download_url=download_url,
        **purl.to_dict(),
    )
    versions = response.get("versions", [])
    for version in versions:
        version_purl = PackageURL(type=purl.type, name=name, version=version.get("num"))
        dl_path = version.get("dl_path")
        if dl_path:
            download_url = f"{base_url}/{dl_path}"
        else:
            download_url = None
        declared_license = version.get("license")

        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            code_view_url=code_view_url,
            download_url=download_url,
            declared_license=declared_license,
            **version_purl.to_dict(),
        )


@router.route("pkg:npm/.*")
def get_npm_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of npm type
    """
    purl = PackageURL.from_string(purl)
    base_path = "http://registry.npmjs.org"
    name = purl.name
    version = purl.version
    api_url = f"{base_path}/{name}"
    response = get_response(api_url)
    vcs_data = response.get("repository") or {}
    bugs = response.get("bugs") or {}

    download_url = f"{base_path}/{name}/-/{name}-{version}.tgz" if version else None
    vcs_url = vcs_data.get("url")
    bug_tracking_url = bugs.get("url")
    license = response.get("license")
    homepage_url = response.get("homepage")

    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        vcs_url=vcs_url,
        bug_tracking_url=bug_tracking_url,
        download_url=download_url,
        declared_license=license,
        **purl.to_dict(),
    )

    versions = response.get("versions", [])
    tags = []
    for num in versions:
        version = versions[num]
        version_purl = PackageURL(
            type=purl.type, name=name, version=version.get("version")
        )
        repository = version.get("repository") or {}
        bugs = response.get("bugs") or {}
        dist = version.get("dist") or {}
        licenses = version.get("licenses") or [{}]
        vcs_url = repository.get("url")
        download_url = dist.get("tarball")
        bug_tracking_url = bugs.get("url")
        declared_license = licenses[0].get("type")

        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            vcs_url=vcs_url,
            bug_tracking_url=bug_tracking_url,
            download_url=download_url,
            declared_license=declared_license,
            **version_purl.to_dict(),
        )


@router.route("pkg:pypi/.*")
def get_pypi_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of npm type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    base_path = "https://pypi.org/pypi"
    api_url = f"{base_path}/{name}/json"
    response = get_response(api_url)
    releases = response.get("releases") or {}
    info = response.get("info") or {}
    homepage_url = info.get("home_page")
    license = info.get("license")
    project_urls = info.get("project_urls") or {}
    code_view_url = get_pypi_codeview_url(project_urls)
    bug_tracking_url = get_pypi_bugtracker_url(project_urls)
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=license,
        **purl.to_dict(),
    )
    for num in releases:
        version_purl = PackageURL(type=purl.type, name=name, version=num)
        release = releases.get(num) or [{}]
        release = release[0]
        download_url = release.get("url")
        yield Package(
            homepage_url=homepage_url,
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            download_url=download_url,
            declared_license=license,
            **version_purl.to_dict(),
        )


@router.route("pkg:github/.*")
def get_github_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of github type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    namespace = purl.namespace
    base_path = "https://api.github.com/repos"
    api_url = f"{base_path}/{namespace}/{name}"
    response = get_response(api_url)
    homepage_url = response.get("homepage")
    vcs_url = response.get("git_url")
    github_url = "https://github.com"
    bug_tracking_url = f"{github_url}/{namespace}/{name}/issues"
    code_view_url = f"{github_url}/{namespace}/{name}"
    license_data = response.get("license") or {}
    declared_license = license_data.get("spdx_id")
    primary_language = response.get("language")
    yield Package(
        homepage_url=homepage_url,
        vcs_url=vcs_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=declared_license,
        primary_language=primary_language,
        **purl.to_dict(),
    )
    release_url = f"{api_url}/releases"
    releases = get_response(release_url)
    for release in releases:
        version = release.get("name")
        version_purl = PackageURL(
            type=purl.type, namespace=namespace, name=name, version=version
        )
        download_url = release.get("tarball_url")
        code_view_url = f"{github_url}/{namespace}/{name}/tree/{version}"
        version_vcs_url = f"{vcs_url}@{version}"
        yield Package(
            homepage_url=homepage_url,
            vcs_url=version_vcs_url,
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            declared_license=declared_license,
            primary_language=primary_language,
            download_url=download_url,
            **version_purl.to_dict(),
        )


@router.route("pkg:bitbucket/.*")
def get_bitbucket_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of bitbucket type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    namespace = purl.namespace
    base_path = "https://api.bitbucket.org/2.0/repositories"
    api_url = f"{base_path}/{namespace}/{name}"
    response = get_response(api_url)
    bitbucket_url = "https://bitbucket.org"
    bug_tracking_url = f"{bitbucket_url}/{namespace}/{name}/issues"
    code_view_url = f"{bitbucket_url}/{namespace}/{name}"
    yield Package(
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        **purl.to_dict(),
    )
    links = response.get("links") or {}
    tags_url = links.get("tags") or {}
    tags_url = tags_url.get("href")
    if not tags_url:
        return []
    tags_data = get_response(tags_url)
    tags = tags_data.get("values") or {}
    for tag in tags:
        version = tag.get("name") or ""
        version_purl = PackageURL(
            type=purl.type, namespace=namespace, name=name, version=version
        )
        download_url = (
            f"{base_path}/{namespace}/{name}/downloads/{name}-{version}.tar.gz"
        )
        code_view_url = f"{bitbucket_url}/{namespace}/{name}/src/{version}"
        yield Package(
            api_url=api_url,
            bug_tracking_url=bug_tracking_url,
            code_view_url=code_view_url,
            download_url=download_url,
            **version_purl.to_dict(),
        )


@router.route("pkg:rubygems/.*")
def get_rubygems_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of rubygems type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    api_url = f"https://rubygems.org/api/v1/gems/{name}.json"
    response = get_response(api_url)
    declared_license = response.get("licenses") or None
    homepage_url = response.get("homepage_uri")
    code_view_url = response.get("source_code_uri")
    bug_tracking_url = response.get("bug_tracker_uri")
    download_url = response.get("gem_uri")
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        bug_tracking_url=bug_tracking_url,
        code_view_url=code_view_url,
        declared_license=declared_license,
        download_url=download_url,
        **purl.to_dict(),
    )


@router.route("pkg:homebrew/.*")
def get_homebrew_data_from_purl(purl):
    """
    Generate `Package` object from the `purl` string of homebrew type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    base_path = "https://formulae.brew.sh/api/formula"
    api_url = f"{base_path}/{name}.json"
    response = get_response(api_url)
    declared_license = response.get("license")
    homepage_url = response.get("homepage")
    urls = response.get("urls") or {}
    stable_url = urls.get("stable") or {}
    download_url = stable_url.get("url")
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        declared_license=declared_license,
        download_url=download_url,
        **purl.to_dict(),
    )
    versions = response.get("versions") or {}
    version_purl = PackageURL(type=purl.type, name=name, version=versions.get("stable"))
    yield Package(
        homepage_url=homepage_url,
        api_url=api_url,
        declared_license=declared_license,
        download_url=download_url,
        **version_purl.to_dict(),
    )
