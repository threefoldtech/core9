

import sys
import os
import time
import re

from js9 import j

if j.core.platformtype.myplatform.isUnix:
    import fcntl

# THIS METHOD IS NOT THREADSAFE

# TODO Fixup singleton-like behavior


class FileLock():

    def __init__(self, fname):
        self._fname = fname
        self._f = None

    def __enter__(self):
        self._f = open(self._fname, 'w')
        fcntl.lockf(self._f, fcntl.LOCK_EX)

    def __exit__(self, *exit):
        try:
            fcntl.lockf(self._f, fcntl.LOCK_UN)
        finally:
            self._f.close()


class Lock:

    _LOCKPATHLINUX = "/tmp/run"
    __LOCKDICTIONARY = {}

    __shared_state = {}

    def __init__(self):
        self.__jslocation__ = "j.tools.lock"
        self.__dict__ = self.__shared_state
        self._LOCKPATHWIN = os.getcwd() + os.sep + 'tmp' + os.sep + 'run' + os.sep

    def lock(self, lockname, locktimeout=60):
        """ Take a system-wide interprocess exclusive lock. Default timeout is 60 seconds """

        if locktimeout < 0:
            raise j.exceptions.RuntimeError(
                "Cannot take lock [%s] with negative timeout [%d]" % (lockname, locktimeout))

        if j.core.platformtype.myplatform.isUnix:
            # linux implementation
            lockfile = self._LOCKPATHLINUX + os.sep + lockname.strip()
            j.sal.fs.createDir(self._LOCKPATHLINUX)
            j.sal.fs.createEmptyFile(lockfile)

            # Do the locking
            lockAcquired = False
            for i in range(locktimeout + 1):
                try:
                    myfile = open(lockfile, "r+")
                    fcntl.flock(myfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    lockAcquired = True
                    self.__LOCKDICTIONARY[lockname] = myfile
                    break
                except IOError:
                    # Did not get the lock :( Sleep 1 second and then retry
                    time.sleep(1)
            if not lockAcquired:
                myfile.close()
                raise j.exceptions.RuntimeError("Cannot acquire lock [%s]" % (lockname))

        elif j.core.platformtype.myplatform.isWindows:
            raise NotImplementedError

    def unlock(self, lockname):
        """ Unlock system-wide interprocess lock """
        if j.core.platformtype.myplatform.isUnix:
            try:
                myfile = self.__LOCKDICTIONARY.pop(lockname)
                fcntl.flock(myfile.fileno(), fcntl.LOCK_UN)
                myfile.close()
            except Exception as exc:
                raise j.exceptions.RuntimeError("Cannot unlock [%s] with ERROR:%s" % (lockname, str(exc)))

        elif j.core.platformtype.myplatform.isWindows:
            raise NotImplementedError


# THIS CODE WAS IN sal.fs, we should only have 1 locking implementation

#
# class LockException(Exception):
#
#     def __init__(self, message='Failed to get lock', innerException=None):
#         if innerException:
#             message += '\nProblem caused by:\n%s' % innerException
#         Exception.__init__(self, message)
#         self.innerException = innerException
#
#
# class LockTimeoutException(LockException):
#
#     def __init__(self, message='Lock request timed out', innerException=None):
#         LockException.__init__(self, message, innerException)
#
#
# class Exceptions:
#     LockException = LockException
#     LockTimeoutException = LockTimeoutException
#
#
# def cleanupString(string, replacewith="_", regex="([^A-Za-z0-9])"):
#     '''Remove all non-numeric or alphanumeric characters'''
#     # Please don't use the logging system here. The logging system
#     # needs this method, using the logging system here would
#     # introduce a circular dependency. Be careful not to call other
#     # functions that use the logging system.
#     return re.sub(regex, replacewith, string)
#
#
# def lock(lockname, locktimeout=60, reentry=False):
#     '''Take a system-wide interprocess exclusive lock. Default timeout is 60 seconds'''
#     logger.debug('Lock with name: %s' % lockname)
#     try:
#         result = lock_(lockname, locktimeout, reentry)
#     except Exception as e:
#         raise LockException(innerException=e)
#     else:
#         if not result:
#             raise LockTimeoutException(
#                 message="Cannot acquire lock [%s]" % (lockname))
#         else:
#             return result
#
#
# def lock_(lockname, locktimeout=60, reentry=False):
#     '''Take a system-wide interprocess exclusive lock.
#
#     Works similar to j.sal.fs.lock but uses return values to denote lock
#     success instead of raising fatal errors.
#
#     This refactoring was mainly done to make the lock implementation easier
#     to unit-test.
#     '''
#     # TODO This no longer uses fnctl on Unix, why?
#     LOCKPATH = os.path.join(j.dirs.TMPDIR, 'locks')
#     lockfile = os.path.join(LOCKPATH, cleanupString(lockname))
#     if reentry:
#         _LOCKDICTIONARY[lockname] = _LOCKDICTIONARY.setdefault(lockname, 0) + 1
#
#     if not islocked(lockname, reentry=reentry):
#         if not j.sal.fs.exists(LOCKPATH):
#             j.sal.fs.createDir(LOCKPATH)
#
#         j.sal.fs.writeFile(lockfile, str(os.getpid()))
#         return True
#     else:
#         locked = False
#         for i in range(locktimeout + 1):
#             locked = islocked(lockname, reentry)
#             if not locked:
#                 break
#             else:
#                 time.sleep(1)
#
#         if not locked:
#             return lock_(lockname, locktimeout, reentry)
#         else:
#             return False
#
#
# def islocked(lockname, reentry=False):
#     '''Check if a system-wide interprocess exclusive lock is set'''
#     isLocked = True
#     LOCKPATH = os.path.join(j.dirs.TMPDIR, 'locks')
#     lockfile = os.path.join(LOCKPATH, cleanupString(lockname))
#
#     try:
#         # read the pid from the lockfile
#         if j.sal.fs.exists(lockfile):
#             pid = open(lockfile, 'rb').read()
#         else:
#             return False
#
#     except (OSError, IOError) as e:
#         # failed to read the lockfile
#         if e.errno != errno.ENOENT:  # exception is not 'file or directory not found' -> file probably locked
#             raise
#     else:
#         # open succeeded without exceptions, continue
#         # check if a process with pid is still running
#         if pid and pid.isdigit():
#             pid = int(pid)
#             if reentry and pid == os.getpid():
#                 return False
#         if j.sal.fs.exists(lockfile) and (not pid or not j.sal.process.isPidAlive(pid)):
#             # cleanup system, pid not active, remove the lockfile
#             j.sal.fs.remove(lockfile)
#             isLocked = False
#     return isLocked
#
#
# def unlock(lockname):
#     """Unlock system-wide interprocess lock"""
#     logger.debug('Unlock with name: %s' % lockname)
#     try:
#         unlock_(lockname)
#     except Exception as msg:
#         raise j.exceptions.RuntimeError(
#             "Cannot unlock [%s] with ERROR: %s" % (lockname, str(msg)))
#
#
# def unlock_(lockname):
#     '''Unlock system-wide interprocess lock
#
#     Works similar to j.sal.fs.unlock but uses return values to denote unlock
#     success instead of raising fatal errors.
#
#     This refactoring was mainly done to make the lock implementation easier
#     to unit-test.
#     '''
#     LOCKPATH = os.path.join(j.dirs.TMPDIR, 'locks')
#     lockfile = os.path.join(LOCKPATH, cleanupString(lockname))
#     if lockname in _LOCKDICTIONARY:
#         _LOCKDICTIONARY[lockname] -= 1
#         if _LOCKDICTIONARY[lockname] > 0:
#             return
#
#     # read the pid from the lockfile
#     if j.sal.fs.exists(lockfile):
#         try:
#             pid = open(lockfile, 'rb').read()
#         except:
#             return
#         if int(pid) != os.getpid():
#             j.errorhandler.raiseWarning(
#                 "Lock %r not owned by this process" % lockname)
#             return
#
#         j.sal.fs.remove(lockfile)
#     # else:
#     #     j.tools.console.echo("Lock %r not found"%lockname)
#
#
# class FileLock:
#
#     '''Context manager for file-based locks
#
#     Context managers were introduced in Python 2.5, see the documentation on the
#     'with' statement for more information:
#
#      * http://www.python.org/dev/peps/pep-0343/
#      * http://pyref.infogami.com/with
#
#     @see: L{lock}
#     @see: L{unlock}
#     '''
#
#     def __init__(self, lock_name, reentry=False, locktimeout=60):
#         self.lock_name = lock_name
#         self.reentry = reentry
#         self.locktimeout = locktimeout
#
#     def __enter__(self):
#         lock(self.lock_name, reentry=self.reentry, locktimeout=self.locktimeout)
#
#     def __exit__(self, *exc_info):
#         unlock(self.lock_name)
#
#     def __call__(self, func):
#         def wrapper(*args, **kwargs):
#             lock(self.lock_name, reentry=self.reentry, locktimeout=self.locktimeout)
#             try:
#                 return func(*args, **kwargs)
#             finally:
#                 unlock(self.lock_name)
#
#         return wrapper
