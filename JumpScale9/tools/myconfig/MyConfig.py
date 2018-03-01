from js9 import j
import os

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
ssh_key_name = ""
"""

FormBuilderBaseClass = j.tools.formbuilder.baseclass_get()


class MyConfigUI(FormBuilderBaseClass):
    """
    This class let the user tune the form displayed during configuration.
    By default configure only show the inputs from the template,
    this class allow to enhance the form with custom inputs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # makes sure that this property is not auto populated, not needed when
        # in form_add_items_pre
        self.auto_disable.append("ssh_key_name")

    def form_add_items_post(self):
        # SSHKEYS
        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        if len(keynames) == 0:
            raise RuntimeError("No ssh key found in ssh-agent. Make sure ssh-agent is running and at least one key is loaded")
        self.widget_add_multichoice("ssh_key_name", keynames)


JSConfigBase = j.tools.configmanager.base_class_config


class MyConfig(JSConfigBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.myconfig"
        JSConfigBase.__init__(self, instance="main", template=TEMPLATE,ui=MyConfigUI)        
