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
# CONDITIONS OF ANY KIND, either express or implied. See tshe License for the
# specific language governing permissions and limitations under the License.

import hashlib
import os
import sys
from functools import partial

import requests
from dateutil import parser as dateparser
from dateutil.parser import ParserError


def fetch_github_tags_gql(purl):
    """
    Yield PackageVersion for given github ``purl`` using the GitHub GQL API.
    """
    for node in fetch_github_tag_nodes(purl):
        name = node["name"]
        target = node["target"]

        # in case the tag is a signed tag, then the commit info is in target['target']
        if "committedDate" not in target:
            target = target["target"]

        committed_date = target.get("committedDate")
        release_date = None
        if committed_date:
            try:
                release_date = dateparser.parse(committed_date)
            except ParserError as e:
                pass

        yield name, release_date


GQL_QUERY = """
query getTags($name: String!, $owner: String!, $after: String)
{
    repository(name: $name, owner: $owner) {
        refs(refPrefix: "refs/tags/", first: 100, after: $after) {
            totalCount
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                name
                target {
                    ... on Commit {
                        committedDate
                    }
                    ... on Tag {
                            target {
                            ... on Commit {
                                committedDate
                            }
                        }
                    }
                }
            }
        }
    }
}"""


def fetch_github_tag_nodes(purl):
    """
    Yield node name/target mappings for Git tags of the ``purl``.

    Each node has this shape:
        {
        "name": "v2.6.24-rc5",
        "target": {
            "target": {
            "committedDate": "2007-12-11T03:48:43Z"
            }
        }
        },
    """
    variables = {
        "owner": purl.namespace,
        "name": purl.name,
    }
    graphql_query = {
        "query": GQL_QUERY,
        "variables": variables,
    }

    while True:
        response = github_response(graphql_query)
        refs = response["data"]["repository"]["refs"]
        for node in refs["nodes"]:
            yield node

        page_info = refs["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        # to fetch next page, we just set the after variable to endCursor
        variables["after"] = page_info["endCursor"]


class GitHubTokenError(Exception):
    pass


class GraphQLError(Exception):
    pass


def get_github_token():
    gh_token = os.environ.get("GH_TOKEN", None)
    if not gh_token:
        from dotenv import load_dotenv

        load_dotenv()
        gh_token = os.environ.get("GH_TOKEN", None)
    return gh_token


def github_response(graphql_query):
    gh_token = get_github_token()

    if not gh_token:
        msg = (
            "GitHub API Token Not Set\n"
            "Set your GitHub token in the GH_TOKEN environment variable."
        )
        raise GitHubTokenError(msg)

    headers = {"Authorization": f"bearer {gh_token}"}

    endpoint = "https://api.github.com/graphql"
    response = requests.post(endpoint, headers=headers, json=graphql_query).json()

    message = response.get("message")
    if message and message == "Bad credentials":
        raise GitHubTokenError(f"Invalid GitHub token: {message}")

    errors = response.get("errors")
    if errors:
        raise GraphQLError(errors)

    return response


def get_github_rest(url):
    headers = None
    gh_token = get_github_token()
    if gh_token:
        headers = {
            "Authorization": f"Bearer {gh_token}",
        }

    return get_response(url, headers)


def get_response(url, headers=None):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()

    raise Exception(f"Failed to fetch: {url}")


def get_text_response(url, headers=None):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.text

    raise Exception(f"Failed to fetch: {url}")


def make_head_request(url, headers=None):
    try:
        resp = requests.head(url, headers=headers)
        return resp
    except:
        raise Exception(f"Failed to fetch: {url}")


def get_hashed_path(name):
    """
    Returns a string with a part of the file path derived from the md5 hash.

    From https://github.com/CocoaPods/cdn.cocoapods.org:
        "There are a set of known prefixes for all Podspec paths, you take the
        name of the pod, create a hash (using md5) of it and take the first
        three characters."

    """
    if not name:
        return
    podname = get_podname_proper(name)
    if name != podname:
        name_to_hash = podname
    else:
        name_to_hash = name

    hash_init = get_first_three_md5_hash_characters(name_to_hash)
    hashed_path = "/".join(list(hash_init))

    return hashed_path


# for FIPS support
sys_v0 = sys.version_info[0]
sys_v1 = sys.version_info[1]
if sys_v0 == 3 and sys_v1 >= 9:
    md5_hasher = partial(hashlib.md5, usedforsecurity=False)
else:
    md5_hasher = hashlib.md5


def get_podname_proper(podname):
    """
    Podnames in cocoapods sometimes are files inside a pods package (like 'OHHTTPStubs/Default')
    This returns proper podname in those cases.
    """
    if "/" in podname:
        return podname.split("/")[0]
    return podname


def get_first_three_md5_hash_characters(podname):
    """
    From https://github.com/CocoaPods/cdn.cocoapods.org:
    "There are a set of known prefixes for all Podspec paths, you take the name of the pod,
    create a hash (using md5) of it and take the first three characters."
    """
    return md5_hasher(podname.encode("utf-8")).hexdigest()[0:3]
