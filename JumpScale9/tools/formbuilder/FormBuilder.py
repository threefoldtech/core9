from js9 import j

import npyscreen


class FormBuilderBaseClass(npyscreen.NPSAppManaged):

    def __init__(self, name, template, config={}):
        self.name = name
        if j.data.types.string.check(template):
            self.template = j.data.serializer.toml.loads(template)
        elif j.data.types.dict.check(template):
            self.template = template
        else:
            raise RuntimeError("template needs to be dict or toml example")
        if not j.data.types.dict.check(config):
            raise RuntimeError("config needs to be dict")
        self.config = config
        self.widgets = {}
        self.widget_types = {}
        self.auto_disable = []
        self.done = []  # which keys are already processed
        npyscreen.NPSApp.__init__(self)
        self.init()

    def main(self):
        # npyscreen.Form.DEFAULT_LINES=200
        self.form = npyscreen.Form(name="Configuration Manager:%s" % self.name,)
        self.form.DEFAULT_LINES = 100
        # from IPython import embed;embed(colors='Linux')

        self.config, errors = j.data.serializer.toml.merge(
            self.template, self.config, listunique=True)

        self.form_add_items_pre()

        for key, val in self.config.items():

            if key in self.auto_disable:
                continue

            ttype = j.data.types.type_detect(val)
            if ttype.NAME in ["string", "integer", "float", "list"]:
                self.widget_add_val(key)
            elif ttype.NAME in ["bool", "boolean"]:
                self.widget_add_boolean(key)
            else:
                raise RuntimeError("did not implement %s" % ttype)

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

        # integrate custom results
        result = self.form_pre_save()
        self.config, errors = j.data.serializer.toml.merge(self.config, result, listunique=True)

        for key, val in self.config.items():

            if key in result:
                continue

            ttype = j.data.types.type_detect(val)

            if ttype.NAME in ["string", "integer", "float", "boolean"]:
                w = self.widgets[key]
                if self.widget_types[key] == "multichoice":
                    # get value from the choice
                    result[key] = w.values[w.value[0]]
                elif self.widget_types[key] == "bool":
                    result[key] = w.value.lower() in ["1", True, "true", "yes", "y"]
                else:
                    result[key] = w.value
            elif ttype.NAME == "list":
                w = self.widgets[key]
                result[key] = ttype.fromString(w.value)
        self.config, errors = j.data.serializer.toml.merge(self.config, result, listunique=True)

    def widget_add(self, name, widget):
        if name not in self.widgets:
            self.widgets[name] = widget

    def widget_add_val(self, name, description=""):
        """
        @param description if empty will be same as name
        """
        if description == "":
            description = name
        description = j.data.text.pad(description, 20)

        val = self.config[name]
        ttype = j.data.types.type_detect(val)
        if ttype.NAME == "list":
            val = ttype.toString(val)
            self.form.add(npyscreen.TitleText, name="%s" % description, editable=False)
            widget = self.form.add(npyscreen.MultiLineEdit, name=name, max_height=6, editable=True, value=val)
            widget.value = str(val)
            self.widget_types[name] = "list"
        else:
            widget = self.form.add(npyscreen.TitleText, name="%s :" % description,)
            widget.value = str(val)
            self.widget_types[name] = "val"
        self.widget_add(name, widget)

    def widget_add_multichoice(self, name, choices, description=""):
        if description == "":
            description = name
        self.widget_types[name] = "multichoice"
        description = j.data.text.pad(description, 20)
        widget = self.form.add_widget(npyscreen.TitleSelectOne, name=description, values=choices)
        # check if there is pre-filled value if yes pre-select it
        if self.config[name] != "":
            if self.config[name] in choices:
                widget.value = choices.index(self.config[name])
        self.widget_add(name, widget)

    def widget_add_boolean(self, name, description="", default=True):
        if description == "":
            description = name
        # self.widget_add_multichoice(name=name,choices=["yes","no"],description=description)
        widget = self.widget_add_val(name=name, description=description)
        self.widget_types[name] = "bool"

    def form_add_items_pre(self):
        pass

    def form_add_items_post(self):
        pass

    def form_pre_save(self):
        return {}

    def init(self):
        pass

    @property
    def yaml(self):
        return j.data.serializer.toml.fancydumps(self.config)

    def __str__(self):
        return self.yaml

    def __repr__(self):
        return self.yaml


class FormBuilderFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.formbuilder"

    def baseclass_get(self):
        """
        returns base class for creating a config object with
        """
        return FormBuilderBaseClass

    def test_interactive(self):  # js9 'j.tools.formbuilder.test_interactive()'

        TEMPLATE = """
        fullname = ""
        email = ""
        login_name = ""
        ssh_key_name = ""
        mylist = [ ]
        will_be_encr_ = ""
        """

        # everything which ends on _ will be encrypted (only works for strings
        # at this point)

        BaseConfig = self.baseclass_get()

        class MyConfig(BaseConfig):

            def init(self):
                # makes sure that this property is not auto populated, not
                # needed when in form_add_items_pre
                self.auto_disable.append("ssh_key_name")

            def form_add_items_post(self):
                # SSHKEYS
                sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
                # keynames = [j.sal.fs.getBaseName(item) for item in
                # j.clients.ssh.ssh_keys_list_from_agent()] #load all ssh keys
                # loaded in mem
                keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
                if len(keynames) == 0:
                    raise RuntimeError("load ssh-agent")
                self.widget_add_multichoice("ssh_key_name", keynames)

            def form_pre_save(self):
                result = {}
                # can overrule some result, will not do here
                return result

        # will create empty config file properly constructed starting from the
        # template
        config, errors = j.data.serializer.toml.merge(TEMPLATE, {})

        # don't start from an empty config
        config["email"] = "someemail@rrr.com"
        config["ssh_key_name"] = [j.sal.fs.getBaseName(item) for item in j.clients.ssh.ssh_keys_list_from_agent()][0]
        for i in range(3):
            config["mylist"].append("this is an item in the list: %s" % i)

        c = MyConfig(name="test", template=TEMPLATE, config=config)
        c.run()

        # don't change it during test
        assert c.config["email"] == "someemail@rrr.com"

        print(c.yaml)
