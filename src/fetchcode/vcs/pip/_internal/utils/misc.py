# Copyright (c) 2008-2020 The pip developers:
# A_Rog, Albert Tugushev, Anthony Sottile, Anubhav Patel, Benoit Pierre,
# BorisZZZ, Chris Hunt, Chris Jerdonek, Christopher Hunt, Dave Jones,
# Deepak Sharma, Donald Stufft, Dustin Ingram, Emil Burzo, Frost Ming,
# GOTO Hayato, Jason R. Coombs, Jeremy Zafran, Krishna Oza, László Kiss Kollár,
# Maxim Kurnikov, Nguyễn Gia Phong, Paul Moore, Pradyun Gedam, Stephan Erb,
# Steve Dower, Stéphane Bidoul (ACSONE), Tom Forbes, Tzu-ping Chung,
# Xavier Fernandez, Yuan Jing Vincent Yan, wim glenn
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import absolute_import

import contextlib
import errno
import getpass
import hashlib
import io
import logging
import os
import posixpath
import shutil
import stat
import sys
from collections import deque

from fetchcode.vcs.pip._vendor import pkg_resources
# NOTE: retrying is not annotated in typeshed as on 2017-07-17, which is
#       why we ignore the type on this import.
from fetchcode.vcs.pip._vendor.retrying import retry  # type: ignore
from fetchcode.vcs.pip._vendor.six import PY2, text_type
from fetchcode.vcs.pip._vendor.six.moves import input, map, zip_longest
from fetchcode.vcs.pip._vendor.six.moves.urllib import parse as urllib_parse
from fetchcode.vcs.pip._vendor.six.moves.urllib.parse import unquote as urllib_unquote

from pip import __version__
from fetchcode.vcs.pip._internal.exceptions import CommandError

from fetchcode.vcs.pip._internal.utils.compat import (
    WINDOWS,
    expanduser,
    stdlib_pkgs,
    str_to_display,
)


if PY2:
    from io import BytesIO as StringIO
else:
    from io import StringIO


__all__ = ['rmtree', 'display_path', 'backup_dir',
           'ask', 'splitext',
           'format_size', 'is_installable_dir',
           'normalize_path',
           'renames', 'get_prog',
           'captured_stdout', 'ensure_dir',
           'get_installed_version', 'remove_auth_from_url']


logger = logging.getLogger(__name__)



def ensure_dir(path):
    # type: (AnyStr) -> None
    """os.path.makedirs without EEXIST."""
    try:
        os.makedirs(path)
    except OSError as e:
        # Windows can raise spurious ENOTEMPTY errors. See #6426.
        if e.errno != errno.EEXIST and e.errno != errno.ENOTEMPTY:
            raise


def get_prog():
    # type: () -> str
    try:
        prog = os.path.basename(sys.argv[0])
        if prog in ('__main__.py', '-c'):
            return "{} -m pip".format(sys.executable)
        else:
            return prog
    except (AttributeError, TypeError, IndexError):
        pass
    return 'pip'


# Retry every half second for up to 3 seconds
@retry(stop_max_delay=3000, wait_fixed=500)
def rmtree(dir, ignore_errors=False):
    # type: (str, bool) -> None
    shutil.rmtree(dir, ignore_errors=ignore_errors,
                  onerror=rmtree_errorhandler)


def rmtree_errorhandler(func, path, exc_info):
    """On Windows, the files in .svn are read-only, so when rmtree() tries to
    remove them, an exception is thrown.  We catch that here, remove the
    read-only attribute, and hopefully continue without problems."""
    try:
        has_attr_readonly = not (os.stat(path).st_mode & stat.S_IWRITE)
    except (IOError, OSError):
        # it's equivalent to os.path.exists
        return

    if has_attr_readonly:
        # convert to read/write
        os.chmod(path, stat.S_IWRITE)
        # use the original function to repeat the operation
        func(path)
        return
    else:
        raise


def path_to_display(path):
    # type: (Optional[Union[str, Text]]) -> Optional[Text]
    """
    Convert a bytes (or text) path to text (unicode in Python 2) for display
    and logging purposes.

    This function should never error out. Also, this function is mainly needed
    for Python 2 since in Python 3 str paths are already text.
    """
    if path is None:
        return None
    if isinstance(path, text_type):
        return path
    # Otherwise, path is a bytes object (str in Python 2).
    try:
        display_path = path.decode(sys.getfilesystemencoding(), 'strict')
    except UnicodeDecodeError:
        # Include the full bytes to make troubleshooting easier, even though
        # it may not be very human readable.
        if PY2:
            # Convert the bytes to a readable str representation using
            # repr(), and then convert the str to unicode.
            #   Also, we add the prefix "b" to the repr() return value both
            # to make the Python 2 output look like the Python 3 output, and
            # to signal to the user that this is a bytes representation.
            display_path = str_to_display('b{!r}'.format(path))
        else:
            # Silence the "F821 undefined name 'ascii'" flake8 error since
            # in Python 3 ascii() is a built-in.
            display_path = ascii(path)  # noqa: F821

    return display_path


def display_path(path):
    # type: (Union[str, Text]) -> str
    """Gives the display value for a given path, making it relative to cwd
    if possible."""
    path = os.path.normcase(os.path.abspath(path))
    if sys.version_info[0] == 2:
        path = path.decode(sys.getfilesystemencoding(), 'replace')
        path = path.encode(sys.getdefaultencoding(), 'replace')
    if path.startswith(os.getcwd() + os.path.sep):
        path = '.' + path[len(os.getcwd()):]
    return path


def backup_dir(dir, ext='.bak'):
    # type: (str, str) -> str
    """Figure out the name of a directory to back up the given dir to
    (adding .bak, .bak2, etc)"""
    n = 1
    extension = ext
    while os.path.exists(dir + extension):
        n += 1
        extension = ext + str(n)
    return dir + extension


def ask_path_exists(message, options):
    # type: (str, Iterable[str]) -> str
    for action in os.environ.get('PIP_EXISTS_ACTION', '').split():
        if action in options:
            return action
    return ask(message, options)


def _check_no_input(message):
    # type: (str) -> None
    """Raise an error if no input is allowed."""
    if os.environ.get('PIP_NO_INPUT'):
        raise Exception(
            'No input was expected ($PIP_NO_INPUT set); question: {}'.format(
                message)
        )


def ask(message, options):
    # type: (str, Iterable[str]) -> str
    """Ask the message interactively, with the given possible responses"""
    while 1:
        _check_no_input(message)
        response = input(message)
        response = response.strip().lower()
        if response not in options:
            print(
                'Your response ({!r}) was not one of the expected responses: '
                '{}'.format(response, ', '.join(options))
            )
        else:
            return response


def ask_input(message):
    # type: (str) -> str
    """Ask for input interactively."""
    _check_no_input(message)
    return input(message)


def ask_password(message):
    # type: (str) -> str
    """Ask for a password interactively."""
    _check_no_input(message)
    return getpass.getpass(message)


def format_size(bytes):
    # type: (float) -> str
    if bytes > 1000 * 1000:
        return '{:.1f} MB'.format(bytes / 1000.0 / 1000)
    elif bytes > 10 * 1000:
        return '{} kB'.format(int(bytes / 1000))
    elif bytes > 1000:
        return '{:.1f} kB'.format(bytes / 1000.0)
    else:
        return '{} bytes'.format(int(bytes))


def tabulate(rows):
    # type: (Iterable[Iterable[Any]]) -> Tuple[List[str], List[int]]
    """Return a list of formatted rows and a list of column sizes.

    For example::

    >>> tabulate([['foobar', 2000], [0xdeadbeef]])
    (['foobar     2000', '3735928559'], [10, 4])
    """
    rows = [tuple(map(str, row)) for row in rows]
    sizes = [max(map(len, col)) for col in zip_longest(*rows, fillvalue='')]
    table = [" ".join(map(str.ljust, row, sizes)).rstrip() for row in rows]
    return table, sizes


def is_installable_dir(path):
    # type: (str) -> bool
    """Is path is a directory containing setup.py or pyproject.toml?
    """
    if not os.path.isdir(path):
        return False
    setup_py = os.path.join(path, 'setup.py')
    if os.path.isfile(setup_py):
        return True
    pyproject_toml = os.path.join(path, 'pyproject.toml')
    if os.path.isfile(pyproject_toml):
        return True
    return False


def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk


def normalize_path(path, resolve_symlinks=True):
    # type: (str, bool) -> str
    """
    Convert a path to its canonical, case-normalized, absolute version.

    """
    path = expanduser(path)
    if resolve_symlinks:
        path = os.path.realpath(path)
    else:
        path = os.path.abspath(path)
    return os.path.normcase(path)


def splitext(path):
    # type: (str) -> Tuple[str, str]
    """Like os.path.splitext, but take off .tar too"""
    base, ext = posixpath.splitext(path)
    if base.lower().endswith('.tar'):
        ext = base[-4:] + ext
        base = base[:-4]
    return base, ext


def renames(old, new):
    # type: (str, str) -> None
    """Like os.renames(), but handles renaming across devices."""
    # Implementation borrowed from os.renames().
    head, tail = os.path.split(new)
    if head and tail and not os.path.exists(head):
        os.makedirs(head)

    shutil.move(old, new)

    head, tail = os.path.split(old)
    if head and tail:
        try:
            os.removedirs(head)
        except OSError:
            pass


def write_output(msg, *args):
    # type: (str, str) -> None
    logger.info(msg, *args)


class FakeFile(object):
    """Wrap a list of lines in an object with readline() to make
    ConfigParser happy."""
    def __init__(self, lines):
        self._gen = (l for l in lines)

    def readline(self):
        try:
            try:
                return next(self._gen)
            except NameError:
                return self._gen.next()
        except StopIteration:
            return ''

    def __iter__(self):
        return self._gen


class StreamWrapper(StringIO):

    @classmethod
    def from_stream(cls, orig_stream):
        cls.orig_stream = orig_stream
        return cls()

    # compileall.compile_dir() needs stdout.encoding to print to stdout
    @property
    def encoding(self):
        return self.orig_stream.encoding


@contextlib.contextmanager
def captured_output(stream_name):
    """Return a context manager used by captured_stdout/stdin/stderr
    that temporarily replaces the sys stream *stream_name* with a StringIO.

    Taken from Lib/support/__init__.py in the CPython repo.
    """
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, StreamWrapper.from_stream(orig_stdout))
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)


def captured_stdout():
    """Capture the output of sys.stdout:

       with captured_stdout() as stdout:
           print('hello')
       self.assertEqual(stdout.getvalue(), 'hello\n')

    Taken from Lib/support/__init__.py in the CPython repo.
    """
    return captured_output('stdout')


def captured_stderr():
    """
    See captured_stdout().
    """
    return captured_output('stderr')


class cached_property(object):
    """A property that is only computed once per instance and then replaces
       itself with an ordinary attribute. Deleting the attribute resets the
       property.

       Source: https://github.com/bottlepy/bottle/blob/0.11.5/bottle.py#L175
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            # We're being accessed from the class itself, not from an object
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def get_installed_version(dist_name, working_set=None):
    """Get the installed version of dist_name avoiding pkg_resources cache"""
    # Create a requirement that we'll look for inside of setuptools.
    req = pkg_resources.Requirement.parse(dist_name)

    if working_set is None:
        # We want to avoid having this cached, so we need to construct a new
        # working set each time.
        working_set = pkg_resources.WorkingSet()

    # Get the installed distribution from our working set
    dist = working_set.find(req)

    # Check to see if we got an installed distribution or not, if we did
    # we want to return it's version.
    return dist.version if dist else None


def consume(iterator):
    """Consume an iterable at C speed."""
    deque(iterator, maxlen=0)


# Simulates an enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = {value: key for key, value in enums.items()}
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


def build_netloc(host, port):
    # type: (str, Optional[int]) -> str
    """
    Build a netloc from a host-port pair
    """
    if port is None:
        return host
    if ':' in host:
        # Only wrap host with square brackets when it is IPv6
        host = '[{}]'.format(host)
    return '{}:{}'.format(host, port)


def build_url_from_netloc(netloc, scheme='https'):
    # type: (str, str) -> str
    """
    Build a full URL from a netloc.
    """
    if netloc.count(':') >= 2 and '@' not in netloc and '[' not in netloc:
        # It must be a bare IPv6 address, so wrap it with brackets.
        netloc = '[{}]'.format(netloc)
    return '{}://{}'.format(scheme, netloc)


def parse_netloc(netloc):
    # type: (str) -> Tuple[str, Optional[int]]
    """
    Return the host-port pair from a netloc.
    """
    url = build_url_from_netloc(netloc)
    parsed = urllib_parse.urlparse(url)
    return parsed.hostname, parsed.port


def split_auth_from_netloc(netloc):
    """
    Parse out and remove the auth information from a netloc.

    Returns: (netloc, (username, password)).
    """
    if '@' not in netloc:
        return netloc, (None, None)

    # Split from the right because that's how urllib.parse.urlsplit()
    # behaves if more than one @ is present (which can be checked using
    # the password attribute of urlsplit()'s return value).
    auth, netloc = netloc.rsplit('@', 1)
    if ':' in auth:
        # Split from the left because that's how urllib.parse.urlsplit()
        # behaves if more than one : is present (which again can be checked
        # using the password attribute of the return value)
        user_pass = auth.split(':', 1)
    else:
        user_pass = auth, None

    user_pass = tuple(
        None if x is None else urllib_unquote(x) for x in user_pass
    )

    return netloc, user_pass


def redact_netloc(netloc):
    # type: (str) -> str
    """
    Replace the sensitive data in a netloc with "****", if it exists.

    For example:
        - "user:pass@example.com" returns "user:****@example.com"
        - "accesstoken@example.com" returns "****@example.com"
    """
    netloc, (user, password) = split_auth_from_netloc(netloc)
    if user is None:
        return netloc
    if password is None:
        user = '****'
        password = ''
    else:
        user = urllib_parse.quote(user)
        password = ':****'
    return '{user}{password}@{netloc}'.format(user=user,
                                              password=password,
                                              netloc=netloc)


def _transform_url(url, transform_netloc):
    """Transform and replace netloc in a url.

    transform_netloc is a function taking the netloc and returning a
    tuple. The first element of this tuple is the new netloc. The
    entire tuple is returned.

    Returns a tuple containing the transformed url as item 0 and the
    original tuple returned by transform_netloc as item 1.
    """
    purl = urllib_parse.urlsplit(url)
    netloc_tuple = transform_netloc(purl.netloc)
    # stripped url
    url_pieces = (
        purl.scheme, netloc_tuple[0], purl.path, purl.query, purl.fragment
    )
    surl = urllib_parse.urlunsplit(url_pieces)
    return surl, netloc_tuple


def _get_netloc(netloc):
    return split_auth_from_netloc(netloc)


def _redact_netloc(netloc):
    return (redact_netloc(netloc),)


def split_auth_netloc_from_url(url):
    # type: (str) -> Tuple[str, str, Tuple[str, str]]
    """
    Parse a url into separate netloc, auth, and url with no auth.

    Returns: (url_without_auth, netloc, (username, password))
    """
    url_without_auth, (netloc, auth) = _transform_url(url, _get_netloc)
    return url_without_auth, netloc, auth


def remove_auth_from_url(url):
    # type: (str) -> str
    """Return a copy of url with 'username:password@' removed."""
    # username/pass params are passed to subversion through flags
    # and are not recognized in the url.
    return _transform_url(url, _get_netloc)[0]


def redact_auth_from_url(url):
    # type: (str) -> str
    """Replace the password in a given url with ****."""
    return _transform_url(url, _redact_netloc)[0]


class HiddenText(object):
    def __init__(
        self,
        secret,    # type: str
        redacted,  # type: str
    ):
        # type: (...) -> None
        self.secret = secret
        self.redacted = redacted

    def __repr__(self):
        # type: (...) -> str
        return '<HiddenText {!r}>'.format(str(self))

    def __str__(self):
        # type: (...) -> str
        return self.redacted

    # This is useful for testing.
    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) != type(other):
            return False

        # The string being used for redaction doesn't also have to match,
        # just the raw, original string.
        return (self.secret == other.secret)

    # We need to provide an explicit __ne__ implementation for Python 2.
    # TODO: remove this when we drop PY2 support.
    def __ne__(self, other):
        # type: (Any) -> bool
        return not self == other


def hide_value(value):
    # type: (str) -> HiddenText
    return HiddenText(value, redacted='****')


def hide_url(url):
    # type: (str) -> HiddenText
    redacted = redact_auth_from_url(url)
    return HiddenText(url, redacted=redacted)


def protect_pip_from_modification_on_windows(modifying_pip):
    # type: (bool) -> None
    """Protection of pip.exe from modification on Windows

    On Windows, any operation modifying pip should be run as:
        python -m pip ...
    """
    pip_names = [
        "pip.exe",
        "pip{}.exe".format(sys.version_info[0]),
        "pip{}.{}.exe".format(*sys.version_info[:2])
    ]

    # See https://github.com/pypa/pip/issues/1299 for more discussion
    should_show_use_python_msg = (
        modifying_pip and
        WINDOWS and
        os.path.basename(sys.argv[0]) in pip_names
    )

    if should_show_use_python_msg:
        new_command = [
            sys.executable, "-m", "pip"
        ] + sys.argv[1:]
        raise CommandError(
            'To modify pip, please run the following command:\n{}'
            .format(" ".join(new_command))
        )


def is_console_interactive():
    # type: () -> bool
    """Is this console interactive?
    """
    return sys.stdin is not None and sys.stdin.isatty()


def hash_file(path, blocksize=1 << 20):
    # type: (str, int) -> Tuple[Any, int]
    """Return (hash, length) for path using hashlib.sha256()
    """

    h = hashlib.sha256()
    length = 0
    with open(path, 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)
    return h, length


def is_wheel_installed():
    """
    Return whether the wheel package is installed.
    """
    try:
        import wheel  # noqa: F401
    except ImportError:
        return False

    return True


def pairwise(iterable):
    # type: (Iterable[Any]) -> Iterator[Tuple[Any, Any]]
    """
    Return paired elements.

    For example:
        s -> (s0, s1), (s2, s3), (s4, s5), ...
    """
    iterable = iter(iterable)
    return zip_longest(iterable, iterable)
