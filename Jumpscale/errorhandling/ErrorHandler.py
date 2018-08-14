import sys
import inspect
import Jumpscale.errorhandling.JSExceptions as JSExceptions


from Jumpscale import j

try:
    import colored_traceback
    colored_traceback.add_hook(always=True)
except ImportError:
    pass

try:
    import pygments.lexers
    from pygments.formatters import get_formatter_by_name
    pygmentsObj = True
except BaseException:
    pygmentsObj = False

import traceback

JSBASE = j.application.jsbase_get_class()


class ErrorHandler(JSBASE):

    def __init__(self):
        self._location = "j.core.errorhandler"
        JSBASE.__init__(self)
        self.setExceptHook()
        self.exceptions = JSExceptions
        j.exceptions = JSExceptions
        self.redis = False

    def redis_enable(self):
        luapath = "%s/errorhandling/eco.lua" % j.dirs.JSLIBDIR
        lua = j.sal.fs.fileGetContents(luapath)
        self._escalateToRedisFunction = j.core.db.register_script(lua)
        self._scriptsInRedis = True

    def _send2Redis(self, eco):
        if self.escalateToRedis:
            self._registerScrips()
            data = eco.json
            res = self._escalateToRedisFunction(
                keys=["queues:eco", "eco:incr", "eco:occurrences", "eco:objects", "eco:last"], args=[eco.key, data])
            res = j.data.serializer.json.loads(res)
            return res
        else:
            return None


    def setExceptHook(self):
        sys.excepthook = self.excepthook
        self.inException = False



    def try_except_error_process(self, err):
        """
        how to use

        try:
            ##do something
        except Exception,e:
            j.errorhandler.try_except_error_process(e)

        """
        ttype, msg, tb = sys.exc_info()
        self.excepthook(ttype, msg, tb)

    def _error_process(self, err):
        #TODO: needs to work with digital me alert manager
        return err

    def excepthook(self, ttype, err, tb):
        """ every fatal error in jumpscale or by python itself will result in an exception
        in this function the exception is caught.
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """

        # print ("jumpscale EXCEPTIONHOOK")
        if self.inException:
            self.logger.error("ERROR IN EXCEPTION HANDLING ROUTINES, which causes recursive errorhandling behavior.")
            self.logger.error(exceptionObject)
            sys.exit(1)
            return

        if "trace_do" in err.__dict__:
            if err.trace_do:
                err._trace = self._trace_get(ttype, err, tb)
                # err.trace_print()
                print(err)
        else:
            tb_text = self._trace_get(ttype, err, tb)
            self._trace_print(tb_text)

        self.inException = True
        self._error_process(err)
        self.inException = False

        sys.exit(1)


    def _filterLocals(self, k, v):
        try:
            k = "%s" % k
            v = "%s" % v
            if k in ["re", "q", "jumpscale", "pprint", "qexec", "jshell", "Shell",
                     "__doc__", "__file__", "__name__", "__package__", "i", "main", "page"]:
                return False
            if v.find("<module") != -1:
                return False
            if v.find("IPython") != -1:
                return False
            if v.find("bpython") != -1:
                return False
            if v.find("click") != -1:
                return False
            if v.find("<built-in function") != -1:
                return False
            if v.find("jumpscale.Shell") != -1:
                return False
        except BaseException:
            return False

        return True

    def _trace_get(self, ttype, err, tb):

        tblist = traceback.format_exception(ttype, err, tb)


        ignore = ["click/core.py", "ipython", "bpython","loghandler","errorhandler"]

        # if self._limit and len(tblist) > self._limit:
        #     tblist = tblist[-self._limit:]
        tb_text = ""
        for item in tblist:
            for ignoreitem in ignore:
                if item.find(ignoreitem) != -1:
                    item = ""
            if item != "":
                tb_text += "%s" % item
        return tb_text

    def _trace_print(self,tb_text):
        if pygmentsObj:
            formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name("vim"))
            lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)  # pytb
            tb_colored = pygments.highlight(tb_text, lexer, formatter)
            sys.stderr.write(tb_colored)
            # print(tb_colored)
        else:
            sys.stderr.write(tb_text)

    # def frames_get(self, tb=None):
    #
    #     def _getitem_from_frame(f_locals, key, default=None):
    #         """
    #         f_locals is not guaranteed to have .get(), but it will always
    #         support __getitem__. Even if it doesnt, we return ``default``.
    #         """
    #         try:
    #             return f_locals[key]
    #         except Exception:
    #             return default
    #
    #     if tb is None:
    #         ttype, msg, tb = sys.exc_info()
    #
    #     if tb is None:
    #         frames = [(item[0], item[2]) for item in inspect.stack()]
    #     else:
    #         frames = []
    #         while tb:  # copied from sentry raven lib (BSD license)
    #             # support for __traceback_hide__ which is used by a few libraries
    #             # to hide internal frames.
    #             f_locals = getattr(tb.tb_frame, 'f_locals', {})
    #             if not _getitem_from_frame(f_locals, '__traceback_hide__'):
    #                 frames.append(
    #                     (tb.tb_frame, getattr(tb, 'tb_lineno', None)))
    #             tb = tb.tb_next
    #         frames.reverse()
    #
    #     result = []
    #     ignore = ["ipython", "errorcondition", "loghandler", "errorhandling"]
    #     for frame, linenr in frames:
    #         name = frame.f_code.co_filename
    #         # print "RRR:%s %s"%(name,linenr)
    #         name = name.lower()
    #         toignore = False
    #         for check in ignore:
    #             if name.find(check) != -1:
    #                 toignore = True
    #         if not toignore:
    #             result.append((frame, linenr))
    #
    #     return result

    # def error_trace_kis_get(self, tb=None):
    #     out = []
    #     nr = 1
    #     filename0 = "unknown"
    #     linenr0 = 0
    #     func0 = "unknown"
    #     frs = self.getFrames(tb=tb)
    #     frs.reverse()
    #     for f, linenr in frs:
    #         try:
    #             code, linenr2 = inspect.findsource(f)
    #         except Exception:
    #             continue
    #         start = max(linenr - 10, 0)
    #         stop = min(linenr + 4, len(code))
    #         code2 = "".join(code[start:stop])
    #         finfo = inspect.getframeinfo(f)
    #         linenr3 = linenr - start - 1
    #         out.append((finfo.filename, finfo.function, linenr3, code2, linenr))
    #         if nr == 1:
    #             filename0 = finfo.filename
    #             linenr0 = linenr
    #             func0 = finfo.function
    #
    #     return out, filename0, linenr0, func0

    def bug_escalate_developer(self, errorConditionObject, tb=None):

        j.logger.enabled = False  # no need to further log, there is error

        tracefile = ""

        def findEditorLinux():
            apps = ["code", "micro"]
            for app in apps:
                try:
                    if j.system.unix.checkApplicationInstalled(app):
                        editor = app
                        return editor
                except BaseException:
                    pass
            return "micro"

        if False and j.application.interactive:

            editor = None
            if j.core.platformtype.myplatform.isLinux:
                #j.tools.console.echo("THIS ONLY WORKS WHEN GEDIT IS INSTALLED")
                editor = findEditorLinux()
            elif j.core.platformtype.myplatform.isWindows:
                editorPath = j.sal.fs.joinPaths(
                    j.dirs.JSBASEDIR, "apps", "wscite", "scite.exe")
                if j.sal.fs.exists(editorPath):
                    editor = editorPath
            tracefile = errorConditionObject.log2filesystem()
            # print "EDITOR FOUND:%s" % editor
            if editor:
                # print errorConditionObject.errormessagepublic
                if tb is None:
                    try:
                        res = j.tools.console.askString(
                            "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace)")
                    except BaseException:                        # print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE
                        # EDITOR"
                        res = "s"
                else:
                    try:
                        res = j.tools.console.askString(
                            "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace, d=debug)")
                    except BaseException:                        # print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE
                        # EDITOR"
                        res = "s"
                if res == "t":
                    cmd = "%s '%s'" % (editor, tracefile)
                    # print "EDITORCMD: %s" %cmd
                    if editor == "less":
                        j.sal.process.executeWithoutPipe(cmd, die=False)
                    else:
                        result, out, err = j.sal.process.execute(
                            cmd, die=False, showout=False)

                j.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    j.tools.console.echo(
                        "Starting pdb, exit by entering the command 'q'")
                    import pdb
                    pdb.post_mortem(tb)
                elif res == "s":
                    # print errorConditionObject
                    j.application.stop(1)
            else:
                # print errorConditionObject
                res = j.tools.console.askString(
                    "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, d=debug)")
                j.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    j.tools.console.echo(
                        "Starting pdb, exit by entering the command 'q'")
                    import pdb
                    pdb.post_mortem()
                elif res == "s":
                    # print eobject
                    j.application.stop(1)

        else:
            # print "ERROR"
            # tracefile=eobject.log2filesystem()
            # print errorConditionObject
            #j.tools.console.echo( "Tracefile in %s" % tracefile)
            j.application.stop(1)

    def halt(self, msg, eco):
        if eco is not None:
            eco = eco.__dict__
        raise HaltException(msg, eco)

    def raiseWarning(self, message, msgpub="", tags="", level=4):
        """
        @param message is the error message which describes the state
        @param msgpub is message we want to show to endcustomers (can include a solution)
        """
        eco = j.errorhandler.getErrorConditionObject(
            ddict={}, msg=message, msgpub=msgpub, category='', level=level, type='WARNING')

        eco.process()
