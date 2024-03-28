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


from pathlib import Path
import requests

data_location = Path(__file__).parent

TEST_SOURCES_INFO = [
    {
        "purl": "pkg:generic/util-linux",
        "sources": [
            {
                "filename": "generic/util-linux/index.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/",
            },
            {
                "filename": "generic/util-linux/0.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.13/",
            },
            {
                "filename": "generic/util-linux/1.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.14/",
            },
            {
                "filename": "generic/util-linux/2.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.15/",
            },
            {
                "filename": "generic/util-linux/3.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.16/",
            },
            {
                "filename": "generic/util-linux/4.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.17/",
            },
            {
                "filename": "generic/util-linux/5.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.18/",
            },
            {
                "filename": "generic/util-linux/6.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.19/",
            },
            {
                "filename": "generic/util-linux/7.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.20/",
            },
            {
                "filename": "generic/util-linux/8.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.21/",
            },
            {
                "filename": "generic/util-linux/9.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.22/",
            },
            {
                "filename": "generic/util-linux/10.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.23/",
            },
            {
                "filename": "generic/util-linux/11.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.24/",
            },
            {
                "filename": "generic/util-linux/12.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.25/",
            },
            {
                "filename": "generic/util-linux/13.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.26/",
            },
            {
                "filename": "generic/util-linux/14.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.27/",
            },
            {
                "filename": "generic/util-linux/15.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.28/",
            },
            {
                "filename": "generic/util-linux/16.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.29/",
            },
            {
                "filename": "generic/util-linux/17.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.30/",
            },
            {
                "filename": "generic/util-linux/18.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.31/",
            },
            {
                "filename": "generic/util-linux/19.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.32/",
            },
            {
                "filename": "generic/util-linux/20.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.33/",
            },
            {
                "filename": "generic/util-linux/21.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.34/",
            },
            {
                "filename": "generic/util-linux/22.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.35/",
            },
            {
                "filename": "generic/util-linux/23.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.36/",
            },
            {
                "filename": "generic/util-linux/24.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.37/",
            },
            {
                "filename": "generic/util-linux/25.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.38/",
            },
            {
                "filename": "generic/util-linux/26.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.39/",
            },
            {
                "filename": "generic/util-linux/27.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/util-linux/v2.40/",
            },
        ],
    },
    {
        "purl": "pkg:generic/busybox",
        "sources": [
            {
                "filename": "generic/busybox/index.html",
                "url": "https://www.busybox.net/downloads/",
            },
        ],
    },
    {
        "purl": "pkg:generic/uclibc",
        "sources": [
            {
                "filename": "generic/uclibc/index.html",
                "url": "https://www.uclibc.org/downloads/",
            },
        ],
    },
    {
        "purl": "pkg:generic/uclibc-ng",
        "sources": [
            {
                "filename": "generic/uclibc-ng/index.html",
                "url": "https://downloads.uclibc-ng.org/releases/",
            },
        ],
    },
    {
        "purl": "pkg:generic/bzip2",
        "sources": [
            {
                "filename": "generic/uclibc-ng/index.html",
                "url": "https://sourceware.org/pub/bzip2/",
            },
            {
                "filename": "generic/uclibc-ng/0.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.0/",
            },
            {
                "filename": "generic/uclibc-ng/1.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.1/",
            },
            {
                "filename": "generic/uclibc-ng/2.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.2/",
            },
            {
                "filename": "generic/uclibc-ng/3.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.3/",
            },
            {
                "filename": "generic/uclibc-ng/4.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.4/",
            },
            {
                "filename": "generic/uclibc-ng/5.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.5/",
            },
            {
                "filename": "generic/uclibc-ng/6.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.6/",
            },
            {
                "filename": "generic/uclibc-ng/7.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.7/",
            },
            {
                "filename": "generic/uclibc-ng/8.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.8/",
            },
            {
                "filename": "generic/uclibc-ng/9.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.9/",
            },
            {
                "filename": "generic/uclibc-ng/10.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.10/",
            },
            {
                "filename": "generic/uclibc-ng/11.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.11/",
            },
            {
                "filename": "generic/uclibc-ng/12.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.12/",
            },
            {
                "filename": "generic/uclibc-ng/13.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.13/",
            },
            {
                "filename": "generic/uclibc-ng/14.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.14/",
            },
            {
                "filename": "generic/uclibc-ng/15.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.15/",
            },
            {
                "filename": "generic/uclibc-ng/16.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.16/",
            },
            {
                "filename": "generic/uclibc-ng/17.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.17/",
            },
            {
                "filename": "generic/uclibc-ng/18.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.18/",
            },
            {
                "filename": "generic/uclibc-ng/19.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.19/",
            },
            {
                "filename": "generic/uclibc-ng/20.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.20/",
            },
            {
                "filename": "generic/uclibc-ng/21.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.21/",
            },
            {
                "filename": "generic/uclibc-ng/22.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.22/",
            },
            {
                "filename": "generic/uclibc-ng/23.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.23/",
            },
            {
                "filename": "generic/uclibc-ng/24.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.24/",
            },
            {
                "filename": "generic/uclibc-ng/25.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.25/",
            },
            {
                "filename": "generic/uclibc-ng/26.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.26/",
            },
            {
                "filename": "generic/uclibc-ng/27.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.27/",
            },
            {
                "filename": "generic/uclibc-ng/28.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.28/",
            },
            {
                "filename": "generic/uclibc-ng/29.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.29/",
            },
            {
                "filename": "generic/uclibc-ng/30.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.30/",
            },
            {
                "filename": "generic/uclibc-ng/31.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.31/",
            },
            {
                "filename": "generic/uclibc-ng/32.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.32/",
            },
            {
                "filename": "generic/uclibc-ng/33.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.33/",
            },
            {
                "filename": "generic/uclibc-ng/34.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.34/",
            },
            {
                "filename": "generic/uclibc-ng/35.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.35/",
            },
            {
                "filename": "generic/uclibc-ng/36.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.36/",
            },
            {
                "filename": "generic/uclibc-ng/37.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.37/",
            },
            {
                "filename": "generic/uclibc-ng/38.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.38/",
            },
            {
                "filename": "generic/uclibc-ng/39.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.39/",
            },
            {
                "filename": "generic/uclibc-ng/40.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.40/",
            },
            {
                "filename": "generic/uclibc-ng/41.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.41/",
            },
            {
                "filename": "generic/uclibc-ng/42.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.42/",
            },
            {
                "filename": "generic/uclibc-ng/43.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.43/",
            },
            {
                "filename": "generic/uclibc-ng/44.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.44/",
            },
            {
                "filename": "generic/uclibc-ng/45.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.45/",
            },
            {
                "filename": "generic/uclibc-ng/46.html",
                "url": "https://downloads.uclibc-ng.org/releases/11.0.46/",
            },
        ],
    },
    {
        "purl": "pkg:generic/openssh",
        "sources": [
            {
                "filename": "generic/openssh/index.html",
                "url": "https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/",
            },
        ],
    },
    {
        "purl": "pkg:generic/dnsmasq",
        "sources": [
            {
                "filename": "generic/dnsmasq/index.html",
                "url": "https://thekelleys.org.uk/dnsmasq/",
            },
        ],
    },
    {
        "purl": "pkg:generic/ebtables",
        "sources": [
            {
                "filename": "generic/ebtables/index.html",
                "url": "https://www.netfilter.org/pub/ebtables/",
            },
        ],
    },
    {
        "purl": "pkg:generic/hostapd",
        "sources": [
            {
                "filename": "generic/hostapd/index.html",
                "url": "https://w1.fi/releases/",
            },
        ],
    },
    {
        "purl": "pkg:generic/dnsmasq",
        "sources": [
            {
                "filename": "generic/dnsmasq/index.html",
                "url": "https://thekelleys.org.uk/dnsmasq/",
            },
        ],
    },
    {
        "purl": "pkg:generic/iproute2",
        "sources": [
            {
                "filename": "generic/iproute2/index.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/",
            },
        ],
    },
    {
        "purl": "pkg:generic/iptables",
        "sources": [
            {
                "filename": "generic/iptables/index.html",
                "url": "https://www.netfilter.org/pub/iptables/",
            },
        ],
    },
    {
        "purl": "pkg:generic/libnl",
        "sources": [
            {
                "filename": "generic/libnl/index.html",
                "url": "https://www.infradead.org/~tgr/libnl/files/",
            },
        ],
    },
    {
        "purl": "pkg:generic/lighttpd",
        "sources": [
            {
                "filename": "generic/lighttpd/index.html",
                "url": "https://download.lighttpd.net/lighttpd/releases-1.4.x/",
            },
        ],
    },
    {
        "purl": "pkg:generic/nftables",
        "sources": [
            {
                "filename": "generic/nftables/index.html",
                "url": "https://www.netfilter.org/pub/nftables/",
            },
        ],
    },
    {
        "purl": "pkg:generic/wpa_supplicant",
        "sources": [
            {
                "filename": "generic/wpa_supplicant/index.html",
                "url": "https://w1.fi/releases/",
            },
        ],
    },
    {
        "purl": "pkg:generic/syslinux",
        "sources": [
            {
                "filename": "generic/syslinux/index.html",
                "url": "https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/",
            },
        ],
    },
    {
        "purl": "pkg:generic/toybox",
        "sources": [
            {
                "filename": "generic/toybox/index.html",
                "url": "http://www.landley.net/toybox/downloads/",
            },
        ],
    },
    {
        "purl": "pkg:generic/dropbear",
        "sources": [
            {
                "filename": "generic/dropbear/index.html",
                "url": "https://matt.ucc.asn.au/dropbear/releases/",
            },
        ],
    },
    {
        "purl": "pkg:gnu/glibc",
        "sources": [
            {
                "filename": "gnu/glibc/index.html",
                "url": "https://ftp.gnu.org/pub/gnu/glibc/",
            },
        ],
    },
    {
        "purl": "pkg:gnu/samba",
        "sources": [
            {
                "filename": "gnu/samba/index.html",
                "url": "https://download.samba.org/pub/samba/stable/",
            },
        ],
    },
    {
        "purl": "pkg:generic/linux",
        "sources": [
            {
                "filename": "generic/linux/index.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/",
            },
            {
                "filename": "generic/linux/0.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v1.0/",
            },
            {
                "filename": "generic/linux/1.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v1.1/",
            },
            {
                "filename": "generic/linux/2.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v1.2/",
            },
            {
                "filename": "generic/linux/3.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v1.3/",
            },
            {
                "filename": "generic/linux/4.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.0/",
            },
            {
                "filename": "generic/linux/5.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.1/",
            },
            {
                "filename": "generic/linux/6.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.2/",
            },
            {
                "filename": "generic/linux/7.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.3/",
            },
            {
                "filename": "generic/linux/8.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.4/",
            },
            {
                "filename": "generic/linux/9.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.5/",
            },
            {
                "filename": "generic/linux/10.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v2.6/",
            },
            {
                "filename": "generic/linux/11.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v3.0/",
            },
            {
                "filename": "generic/linux/12.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v3.x/",
            },
            {
                "filename": "generic/linux/13.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v4.x/",
            },
            {
                "filename": "generic/linux/14.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v5.x/",
            },
            {
                "filename": "generic/linux/15.html",
                "url": "https://cdn.kernel.org/pub/linux/kernel/v6.x/",
            },
        ],
    },
    {
        "purl": "pkg:generic/mtd-utils",
        "sources": [
            {
                "filename": "generic/mtd-utils/index.html",
                "url": "https://infraroot.at/pub/mtd/",
            },
        ],
    },
    {
        "purl": "pkg:generic/barebox",
        "sources": [
            {
                "filename": "generic/barebox/index.html",
                "url": "https://www.barebox.org/download/",
            },
        ],
    },
]


def fetch_mock_data(sources_info=TEST_SOURCES_INFO):
    """
    Fetch mock data for package provided in `sources_info`.
    """
    for package in sources_info:
        for source in package.get("sources"):
            filename = source.get("filename")
            url = source.get("url")

            response = requests.get(url)
            file_path = data_location / filename
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)


def main():
    fetch_mock_data()


if __name__ == "__main__":
    # Script to regenerate mock data for packages module.
    main()
