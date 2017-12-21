from js9 import j

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
ssh_key_name = ""
git_config_url = ""
"""

import npyscreen
class BaseConfig(npyscreen.NPSAppManaged):

    def __init__(self,name,template,config={}):
        self.name=name
        self.template=j.data.serializer.toml.loads(template)
        self.config=config
        self.widgets={}
        self.done=[] #which keys are already processed
        npyscreen.NPSApp.__init__(self)
        self.run()

    def main(self):
        self.form  = npyscreen.Form(name = "Configuration Manager:%s"%self.name,)
        
        self.form_add_items_pre()

        self.config,errors=j.data.serializer.toml.merge(self.template, self.config,listunique=True)        

        for key,val in self.config.items():

            ttype=j.data.types.type_detect(val)
            if ttype.NAME in ["string","integer","float"]:
                print("add widget:%s"%key)
                key1=j.data.text.pad(key,20)
                widget = self.form.add(npyscreen.TitleText, name = "%s :"%key1,)
                widget.value = self.config[key]
                self.widget_add(key,widget)


        self.form_add_items_post()

        # t  = F.add(npyscreen.TitleText, name = "Text:",)
        # fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        # fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        # dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        # s  = F.add(npyscreen.TitleSlider, out_of=12, name = "Slider")
        # ml = F.add(npyscreen.MultiLineEdit,
        #        value = """try typing here!\nMutiline text, press ^R to reformat.\n""",
        #        max_height=5, rely=9)
        # ms = F.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Pick One",
        #         values = ["Option1","Option2","Option3"], scroll_exit=True)
        # ms2= F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Pick Several",
        #         values = ["Option1","Option2","Option3"], scroll_exit=True)

        # This lets the user interact with the Form.
        self.form.edit()
        self.form.exit_editing()
        self.setNextForm(None)
        
        result=self.form_pre_save()
        self.config,errors=j.data.serializer.toml.merge(self.config, result,listunique=True)  

        for key,val in self.config.items():

            if key in result:
                continue

            ttype=j.data.types.type_detect(val)
            if ttype.NAME in ["string","integer","float"]:
                w = self.widgets[key]
                result[key]=w.value

        self.config,errors=j.data.serializer.toml.merge(self.config, result,listunique=True)
        print(self.config)

    def widget_add(self,name,widget):
        self.widgets[name]=widget

    def form_add_items_pre(self):
        pass

    def form_add_items_post(self):
        pass

class MainConfig(BaseConfig):

    def form_add_items_post(self):
        #SSHKEYS
        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        widget = self.form.add_widget(npyscreen.TitleSelectOne, name="YOUR SSH KEY:", values=keynames)
        self.widget_add("ssh_key_name",widget)

    def form_pre_save(self):
        """
        result is what needs to be updated
        """
        result={}
        w=self.widgets["ssh_key_name"]
        if len(w.value)==1:
            item=w.value[0]
            result["ssh_key_name"]=w.values[item]
        return result


class SecretConfigFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"
        config=MainConfig(name="test",template=TEMPLATE,config={}).config
        from IPython import embed;embed(colors='Linux')

    def configure(self, url):
        """
        e.g. the url is e.g. ssh://git@docs.grid.tf:7022/myusername/myconfig.git
        is also stored in the config file in [myconfig] section as giturl & sshkeyname
        
        will checkout your configuration which is encrypted
        
        """

        sc= SecretConfig(secret,sshkeyname=sshkeyname,giturl=giturl)
        sc.start()

    def config_object_baseclass_get(self):
        """
        returns base class for creating a config object with
        """
        return BaseConfig


class SecretConfig:

    def __init__(self, secret, url):
        self.url = url

    def start(self):

        self.init()

    def init(self):
        self.path=j.clients.git.pullGitRepo(url=self.url)

            



        
