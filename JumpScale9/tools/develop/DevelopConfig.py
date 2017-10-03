
from js9 import j
import npyscreen
import curses

##TO TEST IN DOCKER
#ZSSH "js9 'j.tools.develop.config()'"

class ConfigUI(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN",    MainForm)
        self.addForm("SyncCodeForm",    SyncCodeForm)
        self.addForm("FormSelectCodeDirs",       FormSelectCodeDirs, name="Select Codedirs", color="IMPORTANT",)
        self.addForm("FormNodes",     FormNodes, name="Edit Nodes", color="WARNING",)
        self.addForm("FormSelectNodes",       FormSelectNodes, name="Select Nodes", color="IMPORTANT",)
        

    def change_form(self, name):
        # Switch forms.  NB. Do *not* call the .edit() method directly (which
        # would lead to a memory leak and ultimately a recursion error).
        # Instead, use the method .switchForm to change forms.
        self.switchForm(name)

        # By default the application keeps track of every form visited.
        # There's no harm in this, but we don't need it so:
        self.resetHistory()

    def exit_application(self):
        pass


class MyMenu():
    def addMenu(self):
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItem(text='Main', onSelect=self.go2form,
                        shortcut=None, arguments=["MAIN"], keywords=None)    
        self.m1.addItem(text='Select Active Codedirs', onSelect=self.go2form,
                        shortcut=None, arguments=["FormSelectCodeDirs"], keywords=None)
        self.m1.addItem(text='Edit Nodes', onSelect=self.editNodes,
                        shortcut=None, arguments=[], keywords=None)
        self.m1.addItem(text='Select Active Nodes', onSelect=self.go2form,
                        shortcut=None, arguments=["FormSelectNodes"], keywords=None)
        self.m1.addItem(text='Sync Code', onSelect=self.go2form,
                        shortcut=None, arguments=["SyncCodeForm"], keywords=None)
        self.m1.addItem(text='Quit', onSelect=self.exit_application,
                        shortcut=None, keywords=None)


    def go2form(self, name):
        self.parentApp.change_form(name)

    def editNodes(self):


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
    def create(self):
        self.addMenu()
        self.main()

    def main(self):
        # from IPython import embed;embed(colors='Linux')
        self.loginname = self.add_widget(npyscreen.TitleText, name="Your login name:")
        self.loginname.value=j.core.state.configGetFromDict("me","loginname","")
        self.email = self.add_widget(npyscreen.TitleText, name="Your email:")
        self.email.value=j.core.state.configGetFromDict("me","email","")
        self.fullname = self.add_widget(npyscreen.TitleText, name="Full name:")
        self.fullname.value=j.core.state.configGetFromDict("me","fullname","")

        keyname=j.core.state.configGetFromDict("ssh","SSHKEYNAME","")
        keypath="%s/.ssh/%s"%(j.dirs.HOMEDIR,keyname)     

        if not j.sal.fs.exists(keypath):
            sshpath="%s/.ssh"%(j.dirs.HOMEDIR)     
            keynames=[j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath,filter="*.pub")]
            self.sshkeyname = self.add_widget(npyscreen.TitleSelectOne,name="YOUR SSH KEY:",values=keynames)
        else:
            self.sshkeyname = self.add_widget(npyscreen.TitleText, name="YOUR SSH KEY:",value=keyname)


        # from IPython import embed;embed(colors='Linux')

        # self.sshkeypath = self.add_widget(npyscreen.TitleFilenameCombo, name="Your SSH Key Path:",must_exist=True)        
        # keyname=j.core.state.configGetFromDict("ssh","SSHKEYNAME","")
        # if keyname.strip()=="":
        #     keypath="%s/.ssh/??????"%j.dirs.HOMEDIR
        # else:
        #     keypath="%s/.ssh/%s"%(j.dirs.HOMEDIR,keyname)        
        # self.sshkeypath.value=keypath

    def afterEditing(self):
        j.core.state.configSetInDict("me","loginname",self.loginname.value)
        j.core.state.configSetInDict("me","email",self.email.value)
        j.core.state.configSetInDict("me","fullname",self.fullname.value)
        # keyname=j.sal.fs.getBaseName(self.sshkeypath.value)
        j.core.state.configSetInDict("ssh","SSHKEYNAME",self.sshkeyname.value)



class FormSelectCodeDirs(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def main(self):

        wgtree = self.add(npyscreen.MLTreeMultiSelect)

        treedata = npyscreen.NPSTreeData(content='coderoot', selectable=True, ignoreRoot=False)
        treedata.path=""
        for ttype in j.tools.develop.codedirs.tree.children:
            currootTree = treedata.newChild(content=ttype.name, selectable=True, selected=ttype.selected)
            currootTree.path=ttype.path
            for account in ttype.children:
                accTree = currootTree.newChild(content=account.name, selectable=True, selected=account.selected)
                accTree.path=account.path
                for repo in account.children:
                    lowestChild = accTree.newChild(content=repo.name, selectable=True, selected=repo.selected)
                    lowestChild.path=repo.path

        wgtree.values = treedata

        self.wgtree=wgtree

    def afterEditing(self):
        for e in self.wgtree.values:            
            treeItem=j.tools.develop.codedirs.tree.findOne(path=e.path)
            treeItem.selected=e.selected            
        j.tools.develop.codedirs.save()    
        self.parentApp.change_form("MAIN")

class FormSelectNodes(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def main(self):

        wgtree = self.add(npyscreen.MLTreeMultiSelect)

        treedata = npyscreen.NPSTreeData(content='root', selectable=True, ignoreRoot=False)
        treedata.path=""
        
        for cat in j.tools.develop.nodes.tree.children:
            if cat.name=="":
                continue
            currootTree = treedata.newChild(content=cat.name, selectable=True, selected=cat.selected)
            currootTree.path=cat.path
            for node in cat.children:
                nodeTree = currootTree.newChild(content=node.name, selectable=True, selected=node.selected)
                nodeTree.path=node.path

        wgtree.values = treedata

        self.wgtree=wgtree



    def afterEditing(self):
        for e in self.wgtree.values:            
            treeItem=j.tools.develop.nodes.tree.findOne(path=e.path)
            treeItem.selected=e.selected            
        j.tools.develop.nodes.save()
        self.parentApp.change_form("MAIN")

    def addNode(self):
        from IPython import embed;embed(colors='Linux')
        

class FormNodes(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def _processData(self):
        out="\n".join(self.editor.values)
        j.tools.develop.nodes.loadFromText(out)
        j.tools.develop.nodes.save()


    def main(self):
        self.editor = self.add(npyscreen.MultiLineEditableBoxed,
                               max_height=40, rely=5,
                               footer="list of nodes known to the system      (multiline of $name $ipaddr:$port [$category])     $port,category is optional",
                               slow_scroll=False, exit_left=True, exit_right=True)

        data=[]
        for item in j.tools.develop.nodes.nodesGet():
            data.append("%-20s %s:%s [%s]"%(item.name,item.addr,item.port,item.cat))

        self.editor.values=data

        # self.editor.add_handlers({curses.ascii.CR: self.processData, "^S": self.processData})

    def afterEditing(self):
        self._processData()
        self.parentApp.change_form("MAIN")

class SyncCodeForm(npyscreen.FormWithMenus, MyMenu):
    def create(self):
        self.addMenu()
        self.main()

    def main(self):
        self.sync_deletefiles=self.add_widget(npyscreen.TitleText,name="Delete Remove Files During Sync:",value=j.core.state.configGetFromDict("develop","sync_deletefiles",default="1"))
        self.sync_deletefiles.text_field_begin_at=50
        self.sync_deletefiles.use_two_lines=False

        # self.sync_deletefiles=self.add_widget(npyscreen.OptionBoolean)#,name="sync_deletefiles",value=j.core.state.configGetFromDictBool("develop","sync_deletefiles",default=True))
        # self.add(npyscreen.BufferPager,maxlen=1)
        print("\n")

        self.addButton = self.add(npyscreen.ButtonPress,name="SYNC CODE",when_pressed_function=self.sync)


        
    def sync(self):
        j.tools.develop.monitor()

    def afterEditing(self):
        assert str(self.sync_deletefiles.value)=="1" or str(self.sync_deletefiles.value)=="0"
        j.core.state.configSetInDict("develop","sync_deletefiles",self.sync_deletefiles.value)

        # j.core.state.configSetInDict("me","email",self.email.value)
        # j.core.state.configSetInDict("me","fullname",self.fullname.value)
        # # keyname=j.sal.fs.getBaseName(self.sshkeypath.value)
        # j.core.state.configSetInDict("ssh","SSHKEYNAME",self.sshkeyname.value)
