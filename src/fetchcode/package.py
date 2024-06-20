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

import dataclasses
import re
import time
from typing import List
from urllib.parse import urljoin

import htmllistparse
from packageurl import PackageURL
from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

from fetchcode.package_util import GITHUB_SOURCE_BY_PACKAGE
from fetchcode.package_util import IPKG_RELEASES
from fetchcode.package_util import UDHCP_RELEASES
from fetchcode.package_util import ErofsUtilsGitHubSource
from fetchcode.package_util import GitHubSource
from fetchcode.package_util import MiniupnpPackagesGitHubSource
from fetchcode.package_util import OpenSSLGitHubSource
from fetchcode.package_util import construct_cocoapods_package
from fetchcode.package_util import get_cocoapod_tags
from fetchcode.packagedcode_models import Package
from fetchcode.utils import get_hashed_path
from fetchcode.utils import get_response

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
    Yield `Package` object from the `purl` string of github type
    """
    purl = PackageURL.from_string(purl)
    name = purl.name
    namespace = purl.namespace

    gh_package = f"{namespace}/{name}"
    gh_source_class = GITHUB_SOURCE_BY_PACKAGE.get(gh_package, GitHubSource)

    return gh_source_class.get_package_info(purl)


@router.route(
    "pkg:generic/miniupnpc.*",
    "pkg:generic/miniupnpd.*",
    "pkg:generic/minissdpd.*",
)
def get_github_data_for_miniupnp(purl):
    """
    Yield `Package` object for miniupnp packages from GitHub.
    """
    generic_purl = PackageURL.from_string(purl)
    github_repo_purl = PackageURL(
        type="github",
        namespace="miniupnp",
        name="miniupnp",
        version=generic_purl.version,
    )

    return MiniupnpPackagesGitHubSource.get_package_info(
        gh_purl=github_repo_purl, package_name=generic_purl.name
    )


@router.route(
    "pkg:openssl/openssl.*",
)
def get_github_data_for_openssl(purl):
    """
    Yield `Package` object for OpenSSL package from GitHub.
    """
    generic_purl = PackageURL.from_string(purl)
    github_repo_purl = PackageURL(
        type="github",
        namespace="openssl",
        name="openssl",
        version=generic_purl.version,
    )

    return OpenSSLGitHubSource.get_package_info(github_repo_purl)


@router.route("pkg:generic/erofs-utils.*")
def get_github_data_for_erofs_utils(purl):
    """
    Yield `Package` object for erofs-utils package from GitHub.
    """
    generic_purl = PackageURL.from_string(purl)
    github_repo_purl = PackageURL(
        type="github",
        namespace="erofs",
        name="erofs-utils",
        version=generic_purl.version,
    )

    return ErofsUtilsGitHubSource.get_package_info(github_repo_purl)


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


@router.route("pkg:gnu/.*")
def get_gnu_data_from_purl(purl):
    """Generate `Package` object from the `purl` string of gnu type"""
    purl = PackageURL.from_string(purl)
    source_archive_url = f"https://ftp.gnu.org/pub/gnu/{purl.name}/"
    version_regex_template = r"^({}-)(?P<version>[\w.-]*)(.tar.gz)$"
    version_regex = re.compile(version_regex_template.format(re.escape(purl.name)))

    yield from extract_packages_from_listing(
        purl, source_archive_url, version_regex, []
    )


@router.route("pkg:cocoapods/.*")
def get_cocoapods_data_from_purl(purl):
    purl = PackageURL.from_string(purl)
    name = purl.name
    cocoapods_org_url = f"https://cocoapods.org/pods/{name}"
    api = "https://cdn.cocoapods.org"
    hashed_path = get_hashed_path(name)
    hashed_path_underscore = hashed_path.replace("/", "_")
    file_prefix = "all_pods_versions_"
    spec = f"{api}/{file_prefix}{hashed_path_underscore}.txt"
    data_list = get_cocoapod_tags(spec, name)

    for tag in data_list:
        if purl.version and tag != purl.version:
            continue

        gh_repo_owner = None
        gh_repo_name = name
        podspec_api_url = f"https://raw.githubusercontent.com/CocoaPods/Specs/master/Specs/{hashed_path}/{name}/{tag}/{name}.podspec.json"
        podspec_api_response = get_response(podspec_api_url)
        podspec_homepage = podspec_api_response.get('homepage')

        if podspec_homepage.startswith("https://github.com/"):
            podspec_homepage_remove_gh_prefix = podspec_homepage.replace("https://github.com/", "")
            podspec_homepage_split = podspec_homepage_remove_gh_prefix.split("/")
            gh_repo_owner = podspec_homepage_split[0]
            gh_repo_name = podspec_homepage_split[-1]

        tag_pkg = construct_cocoapods_package(
            purl,
            name,
            hashed_path,
            cocoapods_org_url,
            gh_repo_owner,
            gh_repo_name,
            tag
        )

        yield tag_pkg

        if purl.version:
            break


@dataclasses.dataclass
class DirectoryListedSource:
    source_url: str = dataclasses.field(
        default="", metadata={"description": "URL of the directory listing source"}
    )
    is_nested: bool = dataclasses.field(
        default=False,
        metadata={
            "description": "Flag indicating whether the archives are nested within another directory"
        },
    )
    source_archive_regex: re.Pattern = dataclasses.field(
        default=None,
        metadata={
            "description": "Regular expression pattern to match files in the directory listing."
        },
    )
    ignored_files_and_dir: List[str] = dataclasses.field(
        default_factory=list,
        metadata={
            "description": "List of files and directories to ignore in the directory listing."
        },
    )

    @classmethod
    def get_package_info(cls, package_url):
        if cls.is_nested:
            yield from extract_package_from_nested_listing(
                package_url,
                cls.source_url,
                cls.source_archive_regex,
                cls.ignored_files_and_dir,
            )

        else:
            yield from extract_packages_from_listing(
                package_url,
                cls.source_url,
                cls.source_archive_regex,
                cls.ignored_files_and_dir,
            )


# The udhcp is no longer maintained as a standalone project.
# It has been fully integrated into busybox.
class UdhcpDirectoryListedSource(DirectoryListedSource):
    source_url = (
        "https://web.archive.org/web/20021209021312/http://udhcp.busybox.net/source/"
    )

    @classmethod
    def get_package_info(cls, package_url):

        version = package_url.version
        if version and version in UDHCP_RELEASES:
            archive = UDHCP_RELEASES[version]
            yield Package(
                homepage_url=cls.source_url,
                download_url=archive["url"],
                release_date=archive["date"],
                **package_url.to_dict(),
            )

        else:
            for version, data in UDHCP_RELEASES.items():
                purl = PackageURL(type="generic", name="udhcp", version=version)
                yield Package(
                    homepage_url=cls.source_url,
                    download_url=data["url"],
                    release_date=data["date"],
                    **purl.to_dict(),
                )


class IpkgDirectoryListedSource(DirectoryListedSource):
    source_url = "https://web.archive.org/web/20090326020239/http://handhelds.org/download/packages/ipkg/"
    is_nested = False
    source_archive_regex = re.compile(
        r"^(ipkg[-_])(?P<version>[\w.-]*)(_arm.ipk|.tar.gz)$"
    )
    ignored_files_and_dir = []

    @classmethod
    def get_package_info(cls, package_url):

        version = package_url.version
        if version and version in IPKG_RELEASES:
            archive = IPKG_RELEASES[version]
            yield Package(
                homepage_url=cls.source_url,
                download_url=archive["url"],
                release_date=archive["date"],
                **package_url.to_dict(),
            )

        else:
            for version, data in IPKG_RELEASES.items():
                purl = PackageURL(type="generic", name="ipkg", version=version)
                yield Package(
                    homepage_url=cls.source_url,
                    download_url=data["url"],
                    release_date=data["date"],
                    **purl.to_dict(),
                )


class UtilLinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/"
    is_nested = True
    # Source archive ex: util-linux-1.2.3.tar.gz
    source_archive_regex = re.compile(
        r"^(util-linux-|util-linux-ng-)(?P<version>[\w.-]*)(.tar.gz)$"
    )
    ignored_files_and_dir = []


class BusyBoxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.busybox.net/downloads/"
    # Source archive ex: busybox-1.2.3.tar.bz2
    source_archive_regex = re.compile(r"^(busybox-)(?P<version>[\w.-]*)(.tar.bz2)$")
    is_nested = False
    ignored_files_and_dir = []


class UclibcDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.uclibc.org/downloads/"
    # Source archive ex: uClibc-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(uClibc-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class UclibcNGDirectoryListedSource(DirectoryListedSource):
    source_url = "https://downloads.uclibc-ng.org/releases/"
    # Source archive ex: uClibc-ng-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(uClibc-ng-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = True
    ignored_files_and_dir = []


class Bzip2DirectoryListedSource(DirectoryListedSource):
    source_url = "https://sourceware.org/pub/bzip2/"
    # Source archive ex: bzip2-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(bzip2-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class OpenSSHDirectoryListedSource(DirectoryListedSource):
    source_url = "https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/"
    # Source archive ex: openssh-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(openssh-)(?P<version>[\w.-]*)(.tgz|.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class DnsmasqDirectoryListedSource(DirectoryListedSource):
    source_url = "https://thekelleys.org.uk/dnsmasq/"
    # Source archive ex: dnsmasq-1.2.3.tar.gz
    source_archive_regex = re.compile(
        r"^(dnsmasq-)(?P<version>[\w.-]*)(.tar.xz|.tar.gz)$"
    )
    is_nested = False
    ignored_files_and_dir = []


class EbtablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/ebtables/"
    # Source archive ex: ebtables-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(ebtables-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class HostapdDirectoryListedSource(DirectoryListedSource):
    source_url = "https://w1.fi/releases/"
    # Source archive ex: hostapd-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(hostapd-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class Iproute2DirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/"
    source_archive_regex = re.compile(
        # Source archive ex: iproute2-1.2.3.tar.gz
        r"^(iproute2-)(?P<version>[\w.-]*)(.tar.xz|.tar.gz)$"
    )
    is_nested = False
    ignored_files_and_dir = []


class IptablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/iptables/"
    # Source archive ex: iptables-1.2.3.tar.bz2
    source_archive_regex = re.compile(r"^(iptables-)(?P<version>[\w.-]*)(.tar.bz2)$")
    is_nested = False
    ignored_files_and_dir = []


class LibnlDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.infradead.org/~tgr/libnl/files/"
    # Source archive ex: libnl-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(libnl-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class LighttpdDirectoryListedSource(DirectoryListedSource):
    source_url = "https://download.lighttpd.net/lighttpd/releases-1.4.x/"
    # Source archive ex: lighttpd-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(lighttpd-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class NftablesDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.netfilter.org/pub/nftables/"
    # Source archive ex: nftables-1.2.3.tar.bz2
    source_archive_regex = re.compile(
        r"^(nftables-)(?P<version>[\w.-]*)(.tar.xz|.tar.bz2)$"
    )
    is_nested = False
    ignored_files_and_dir = []


class WpaSupplicantDirectoryListedSource(DirectoryListedSource):
    source_url = "https://w1.fi/releases/"
    # Source archive ex: wpa_supplicant-1.2.3.tar.gz
    source_archive_regex = re.compile(
        r"^(wpa_supplicant-)(?P<version>[\w.-]*)(.tar.gz)$"
    )
    is_nested = False
    ignored_files_and_dir = []


class SyslinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/"
    # Source archive ex: syslinux-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(syslinux-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class SyslinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/"
    # Source archive ex: syslinux-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(syslinux-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class ToyboxDirectoryListedSource(DirectoryListedSource):
    source_url = "http://www.landley.net/toybox/downloads/"
    # Source archive ex: toybox-1.2.3.tar.gz
    source_archive_regex = re.compile(
        r"^(toybox-)(?P<version>[\w.-]*)(.tar.gz|.tar.bz2)$"
    )
    is_nested = False
    ignored_files_and_dir = []


class DropbearDirectoryListedSource(DirectoryListedSource):
    source_url = "https://matt.ucc.asn.au/dropbear/releases/"
    # Source archive ex: dropbear-1.2.3.tar.bz2
    source_archive_regex = re.compile(
        r"^(dropbear-)(?P<version>[\w.-]*)(.tar.bz2|_i386.deb)$"
    )
    is_nested = False
    ignored_files_and_dir = [
        "dropbear-0.44test1.tar.bz2",
        "dropbear-0.44test1.tar.gz",
        "dropbear-0.44test2.tar.bz2",
        "dropbear-0.44test2.tar.gz",
        "dropbear-0.44test3.tar.bz2",
        "dropbear-0.44test3.tar.gz",
        "dropbear-0.44test4.tar.bz2",
        "dropbear-0.44test4.tar.gz",
    ]


class SambaDirectoryListedSource(DirectoryListedSource):
    source_url = "https://download.samba.org/pub/samba/stable/"
    # Source archive ex: samba-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(samba-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = False
    ignored_files_and_dir = []


class MtdUtilsDirectoryListedSource(DirectoryListedSource):
    source_url = "https://infraroot.at/pub/mtd/"
    # Source archive ex: mtd-utils-1.2.3.tar.bz2
    source_archive_regex = re.compile(r"^(mtd-utils-)(?P<version>[\w.-]*)(.tar.bz2)$")
    is_nested = False
    ignored_files_and_dir = []


class BareboxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://www.barebox.org/download/"
    # Source archive ex: barebox-1.2.3.tar.bz2
    source_archive_regex = re.compile(r"^(barebox-)(?P<version>[\w.-]*)(.tar.bz2)$")
    is_nested = False
    ignored_files_and_dir = []


class LinuxDirectoryListedSource(DirectoryListedSource):
    source_url = "https://mirrors.edge.kernel.org/pub/linux/kernel/"
    # Source archive ex: linux-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(linux-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = True
    ignored_files_and_dir = [
        "Historic/",
        "SillySounds/",
        "crypto/",
        "firmware/",
        "next/",
        "people/",
        "ports/",
        "projects/",
        "testing/",
        "tools/",
        "uemacs/",
    ]


class E2fsprogsDirectoryListedSource(DirectoryListedSource):
    source_url = (
        "https://mirrors.edge.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/"
    )
    # Source archive ex: e2fsprogs-1.2.3.tar.gz
    source_archive_regex = re.compile(r"^(e2fsprogs-)(?P<version>[\w.-]*)(.tar.gz)$")
    is_nested = True
    ignored_files_and_dir = ["testing/"]


DIR_SUPPORTED_PURLS = [
    "pkg:generic/busybox.*",
    "pkg:generic/bzip2.*",
    "pkg:generic/dnsmasq.*",
    "pkg:generic/dropbear.*",
    "pkg:generic/ebtables.*",
    "pkg:generic/hostapd.*",
    "pkg:generic/iproute2.*",
    "pkg:generic/iptables.*",
    "pkg:generic/libnl.*",
    "pkg:generic/lighttpd.*",
    "pkg:generic/nftables.*",
    "pkg:generic/openssh.*",
    "pkg:generic/samba.*",
    "pkg:generic/syslinux.*",
    "pkg:generic/toybox.*",
    "pkg:generic/uclibc",
    "pkg:generic/uclibc@.*",
    "pkg:generic/uclibc-ng.*",
    "pkg:generic/util-linux.*",
    "pkg:generic/wpa_supplicant.*",
    "pkg:generic/ipkg.*",
    "pkg:generic/mtd-utils.*",
    "pkg:generic/barebox.*",
    "pkg:generic/linux.*",
    "pkg:generic/e2fsprogs.*",
    "pkg:generic/udhcp.*",
]

DIR_LISTED_SOURCE_BY_PACKAGE_NAME = {
    "busybox": BusyBoxDirectoryListedSource,
    "bzip2": Bzip2DirectoryListedSource,
    "dnsmasq": DnsmasqDirectoryListedSource,
    "dropbear": DropbearDirectoryListedSource,
    "ebtables": EbtablesDirectoryListedSource,
    "hostapd": HostapdDirectoryListedSource,
    "iproute2": Iproute2DirectoryListedSource,
    "iptables": IptablesDirectoryListedSource,
    "libnl": LibnlDirectoryListedSource,
    "lighttpd": LighttpdDirectoryListedSource,
    "nftables": NftablesDirectoryListedSource,
    "openssh": OpenSSHDirectoryListedSource,
    "samba": SambaDirectoryListedSource,
    "syslinux": SyslinuxDirectoryListedSource,
    "toybox": ToyboxDirectoryListedSource,
    "uclibc": UclibcDirectoryListedSource,
    "uclibc-ng": UclibcNGDirectoryListedSource,
    "util-linux": UtilLinuxDirectoryListedSource,
    "wpa_supplicant": WpaSupplicantDirectoryListedSource,
    "ipkg": IpkgDirectoryListedSource,
    "mtd-utils": MtdUtilsDirectoryListedSource,
    "barebox": BareboxDirectoryListedSource,
    "linux": LinuxDirectoryListedSource,
    "e2fsprogs": E2fsprogsDirectoryListedSource,
    "udhcp": UdhcpDirectoryListedSource,
}


@router.route(*DIR_SUPPORTED_PURLS)
def get_htmllisting_data_from_purl(purl):
    """Generate `Package` object from the `purl` having directory listed source"""
    package_url = PackageURL.from_string(purl)
    return DIR_LISTED_SOURCE_BY_PACKAGE_NAME[package_url.name].get_package_info(
        package_url
    )


def get_packages_from_listing(purl, source_archive_url, regex, ignored_files_and_dir):
    """
    Return list of package data from a directory listing based on the specified regex.
    """
    _, listing = htmllistparse.fetch_listing(source_archive_url)

    packages = []
    for file in listing:
        match = regex.match(file.name)
        if not match or file.name in ignored_files_and_dir:
            continue

        version = match.group("version")
        version = version.strip("v").strip()
        if not version or not version[0].isdigit():
            continue

        modified_time = file.modified
        date = time.strftime("%Y-%m-%dT%H:%M:%S", modified_time)

        download_url = urljoin(source_archive_url, file.name)
        package_url = PackageURL(
            type=purl.type,
            namespace=purl.namespace,
            name=purl.name,
            version=version,
        )
        packages.append(
            Package(
                homepage_url=source_archive_url,
                download_url=download_url,
                release_date=date,
                **package_url.to_dict(),
            )
        )

    return packages


def extract_packages_from_listing(
    purl, source_archive_url, regex, ignored_files_and_dir
):
    """
    Yield package data from a directory listing for the given source_archive_url.
    """
    for package in get_packages_from_listing(
        purl, source_archive_url, regex, ignored_files_and_dir
    ):
        # Don't yield all packages when a specific version is requested.
        if purl.version and package.version != purl.version:
            continue

        yield package

        # If a version is specified in purl and we have found a matching package,
        # we don't need to continue searching.
        if purl.version:
            break


def extract_package_from_nested_listing(purl, source_url, regex, ignored_files_and_dir):
    """
    Yield package data from a nested directory listing for the given source_url.
    """
    _, listing = htmllistparse.fetch_listing(source_url)
    for directory in listing:
        if not directory.name.endswith("/") or directory.name in ignored_files_and_dir:
            continue

        directory_url = urljoin(source_url, directory.name)

        for package in get_packages_from_listing(
            purl, directory_url, regex, ignored_files_and_dir
        ):
            # Don't yield all packages when a specific version is requested.
            if purl.version and package.version != purl.version:
                continue

            yield package

            # If a version is specified in purl and we have found a matching package,
            # we don't need to continue searching.
            if purl.version:
                return
