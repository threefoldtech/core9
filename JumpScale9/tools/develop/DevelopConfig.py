
from js9 import j
import npyscreen
import curses


class ConfigUI(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN",    MainForm)
        self.addForm("FormSelectCodeDirs",       FormSelectCodeDirs, name="Select Codedirs", color="IMPORTANT",)
        self.addForm("FormNodes",     FormNodes, name="Screen 2", color="WARNING",)

    def change_form(self, name):
        # Switch forms.  NB. Do *not* call the .edit() method directly (which
        # would lead to a memory leak and ultimately a recursion error).
        # Instead, use the method .switchForm to change forms.
        self.switchForm(name)

        # By default the application keeps track of every form visited.
        # There's no harm in this, but we don't need it so:
        self.resetHistory()

        


class MyMenu():
    def addMenu(self):
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItem(text='Select Active Codedirs', onSelect=self.go2form,
                        shortcut=None, arguments=["FormSelectCodeDirs"], keywords=None)
        self.m1.addItem(text='Specify Active Nodes', onSelect=self.go2form,
                        shortcut=None, arguments=["FormNodes"], keywords=None)

    def go2form(self, name):
        self.parentApp.change_form(name)

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def whenDisplayText(self, argument):
        npyscreen.notify_confirm(argument)

    def whenJustBeep(self):
        curses.beep()

    def exit_application(self):
        curses.beep()
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


class MainForm(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()


class FormSelectCodeDirs(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def main(self):

        wgtree = self.add(npyscreen.MLTreeMultiSelect)

        treedata = npyscreen.NPSTreeData(content='coderoot', selectable=True, ignoreRoot=False)

        for ttype in self.parentApp.codedirs.tree.children:
            currootTree = treedata.newChild(content=ttype.name, selectable=True, selected=False)
            for account in ttype.children:
                accTree = currootTree.newChild(content=account.name, selectable=True, selected=False)
                for repo in account.children:
                    lowestChild = accTree.newChild(content=repo.name, selectable=True, selected=False)

        wgtree.values = treedata

        # self.edit()

        # RETURN = wgtree.values
        # return wgtree.get_selected_objects()


class FormNodes(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def processData(self, *args):
        res = []
        for line in self.editor.values:
            if line.strip() == "":
                continue
            try:
                name, line = line.split(" ", 1)
            except:
                continue

            if "#" in line:
                line, remark = line.split("#", 1)
                remark = remark.strip()
            else:
                remark = ""

            name = name.lower()
            if ":" in line:
                addr, port = line.split(":")
                addr = addr.strip()
                port = port.strip()
            else:
                addr = line.strip()
                port = "22"

            res.append("%-20s %s:%s" % (name, addr, port))

        res.sort()

        self.editor.values = res
        self.editor.display()

    def main(self):
        self.codedirs = j.tools.develop.codedirs
        # self.add(npyscreen.TitleText, name="autocomplete to make list smaller: ",
        #          value="", value_changed_callback=self.changedAutocomplete)
        # self.add(npyscreen.Autocomplete, name="autocomplete", value_changed_callback=self.changedAutocomplete)
        self.editor = self.add(npyscreen.MultiLineEditableBoxed,
                               max_height=50, rely=5,
                               footer="list of nodes known to the system      (multiline of $name $ipaddr:$port)     $port is optional, ^s will format.",
                               slow_scroll=False, exit_left=True, exit_right=True)

        self.editor.add_handlers({curses.ascii.CR: self.processData, "^S": self.processData})

    def changedAutocomplete(self, widget):
        self.editor.value = widget.value

    def afterEditing(self):
        self.processData()
        self.parentApp.setNextFormPrevious()
