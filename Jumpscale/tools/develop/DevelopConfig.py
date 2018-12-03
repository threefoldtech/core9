
from jumpscale import j
import npyscreen
import curses

# TO TEST IN DOCKER
# ZSSH "js_shell 'j.tools.develop.config()'"

JSBASE = j.application.jsbase_get_class()


class ConfigUI(npyscreen.NPSAppManaged, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def onStart(self):
        # self.addForm("MAIN", MainForm)
        self.addForm("MAIN", FormSelectCodeDirs,
                     name="Select Codedirs", color="IMPORTANT",)
        self.addForm("FormSelectNodes", FormSelectNodes,
                     name="Select Nodes", color="IMPORTANT",)
        # self.addForm("SyncCodeForm", SyncCodeForm)
        # self.addForm("FormNodes", FormNodes,
        #              name="Edit Nodes", color="WARNING",)

    def change_form(self, name):
        # Switch forms.  NB. Do *not* call the .edit() method directly (which
        # would lead to a memory leak and ultimately a recursion error).
        # Instead, use the method .switchForm to change forms.
        self.switchForm(name)

        # By default the application keeps track of every form visited.
        # There's no harm in this, but we don't need it so:
        self.resetHistory()

    def exit_application(self):
        # TODO:*1 does not work well yet
        pass


class MyMenu(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def addMenu(self):
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItem(text='Main', onSelect=self.go2form,
                        shortcut=None, arguments=["MAIN"], keywords=None)
        self.m1.addItem(text='Select Active Codedirs', onSelect=self.go2form,
                        shortcut=None, arguments=["FormSelectCodeDirs"], keywords=None)
        self.m1.addItem(text='Edit Jumpscale Core Configfile', onSelect=self.editConfigFileJS,
                        shortcut=None, arguments=[], keywords=None)
        self.m1.addItem(text='Select Active Nodes', onSelect=self.go2form,
                        shortcut=None, arguments=["FormSelectNodes"], keywords=None)
        # self.m1.addItem(text='Sync Code', onSelect=self.go2form,
        #                 shortcut=None, arguments=["SyncCodeForm"], keywords=None)
        self.m1.addItem(text='Quit', onSelect=self.exit_application,
                        shortcut=None, keywords=None)

    def go2form(self, name):
        self.parentApp.change_form(name)

    def editConfigFileJS(self):
        j.tools.prefab.local.apps.microeditor.install()
        j.sal.process.executeInteractive(
            "micro %s" % j.core.state.configJSPath)
        j.core.state.load()

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def whenDisplayText(self, argument):
        npyscreen.notify_confirm(argument)

    def whenJustBeep(self):
        curses.beep()

    def exit_application(self):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()
        self.parentApp.exit_application()


class MainForm(npyscreen.FormWithMenus, MyMenu):
    def __init__(self):
        MyMenu.__init__(self)

    def create(self):
        self.addMenu()
        self.main()

    def main(self):
        self.add_widget(npyscreen.TitleText, name="Use this to configure your nodes, codedirs and jsconfig")
        # self.email = self.add_widget(npyscreen.TitleText, name="Your email:")
        # self.fullname = self.add_widget(npyscreen.TitleText, name="Full name:")
        # self.myconfig_url = self.add_widget(npyscreen.TitleText, name="My Config git URL:")

        # self.loginname.value = j.core.state.configMe["me"].get("loginname", "")
        # self.email.value = j.core.state.configMe["me"].get("email", "")
        # self.fullname.value = j.core.state.configMe["me"].get("fullname", "")

        # self.myconfig_url.value = j.core.state.configMe["me"].get("fullname", "")

        # # keyname = j.core.state.configMe["ssh"].get("sshkeyname", "")

        # # keypath = "%s/.ssh/%s" % (j.dirs.HOMEDIR, keyname)
        # # if not j.sal.fs.exists(keypath):

        # sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        # keynames = [j.sal.fs.getBaseName(
        #     item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        # self.sshkeyname = self.add_widget(
        #     npyscreen.TitleSelectOne, name="YOUR SSH KEY:", values=keynames)

        # sshkeyname = j.core.state.configMe["ssh"]["sshkeyname"]

        # if keynames.count(sshkeyname) > 0:
        #     pos = keynames.index(sshkeyname)
        #     self.sshkeyname.set_value(pos)

        # self.keynames = keynames

        # def afterEditing(self):
        #     j.core.state.configMe["me"]["loginname"] = self.loginname.value
        #     j.core.state.configMe["me"]["email"] = self.email.value
        #     j.core.state.configMe["me"]["fullname"] = self.fullname.value
        #     if len(self.sshkeyname.value) == 1:
        #         j.core.state.configMe["ssh"]["sshkeyname"] = self.keynames[self.sshkeyname.value[0]]

        #     j.core.state.configSave()


class FormSelectCodeDirs(npyscreen.FormWithMenus, MyMenu):
    def __init__(self):
        MyMenu.__init__(self)

    def create(self):
        self.addMenu()
        self.main()

    def main(self):
        wgtree = self.add(npyscreen.MLTreeMultiSelect)

        treedata = npyscreen.NPSTreeData(
            content='coderoot', selectable=True, ignoreRoot=False)
        treedata.path = ""
        for ttype in j.tools.develop.codedirs.tree.children:
            currootTree = treedata.newChild(
                content=ttype.name, selectable=True, selected=ttype.selected)
            currootTree.path = ttype.path
            for account in ttype.children:
                accTree = currootTree.newChild(
                    content=account.name, selectable=True, selected=account.selected)
                accTree.path = account.path
                for repo in account.children:
                    lowestChild = accTree.newChild(
                        content=repo.name, selectable=True, selected=repo.selected)
                    lowestChild.path = repo.path

        wgtree.values = treedata
        self.wgtree = wgtree

    def afterEditing(self):
        for e in self.wgtree.values:
            treeItem = j.tools.develop.codedirs.tree.findOne(path=e.path)
            treeItem.selected = e.selected
        j.tools.develop.codedirs.save()
        self.parentApp.change_form("FormSelectNodes")


class FormSelectNodes(npyscreen.FormWithMenus, MyMenu):
    def __init__(self):
        MyMenu.__init__(self)

    def create(self):
        self.addMenu()
        self.main()

    def main(self):

        wgtree = self.add(npyscreen.MLTreeMultiSelect)

        treedata = npyscreen.NPSTreeData(
            content='root', selectable=True, ignoreRoot=False)
        treedata.path = ""
        for cat in j.tools.nodemgr.tree.children:
            if cat.name == "":
                continue
            currootTree = treedata.newChild(
                content='{} ({})'.format(cat.name, cat.cat), selectable=True, selected=cat.selected)
            currootTree.path = cat.path
            for node in cat.children:
                nodeTree = currootTree.newChild(
                    content='{} ({})'.format(node.name, node.cat), selectable=True, selected=node.selected)
                nodeTree.path = node.path

        wgtree.values = treedata
        self.wgtree = wgtree

    def afterEditing(self):
        for e in self.wgtree.values:
            treeItem = j.tools.nodemgr.tree.findOne(path=e.path)
            treeItem.selected = e.selected
            if treeItem.cat != None:
                n = j.tools.nodemgr.get(treeItem.name)
                if n.selected != treeItem.selected:
                    n.selected = treeItem.selected
                    n.save()
        self.parentApp.change_form(None)


# class SyncCodeForm(npyscreen.FormWithMenus, MyMenu):
#     def create(self):
#         self.addMenu()
#         self.main()

#     def main(self):
#         self.sync_deletefiles = self.add_widget(npyscreen.TitleText, name="Delete Remove Files During Sync:",
#                                                 value=j.core.state.stateGetFromDict("develop", "sync_deletefiles", default="1"))
#         self.sync_deletefiles.text_field_begin_at = 50
#         self.sync_deletefiles.use_two_lines = False

#         print("\n")

#         self.addButton = self.add(
#             npyscreen.ButtonPress, name="SYNC CODE", when_pressed_function=self.sync)

#     def sync(self):
#         j.tools.develop.monitor()

#     def afterEditing(self):
#         assert str(self.sync_deletefiles.value) == "1" or str(
#             self.sync_deletefiles.value) == "0"
#         j.core.state.stateSetInDict(
#             "develop", "sync_deletefiles", self.sync_deletefiles.value)
