from js9 import j

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MyFileSystemEventHandler(FileSystemEventHandler):

    def handler(self, event, action="copy"):
        changedfile = event.src_path
        if event.is_directory:
            if changedfile.find("/.git") != -1:
                return
            elif changedfile.find("/__pycache__/") != -1:
                return
            if event.event_type == "modified":
                return
            j.tools.develop.sync()
        else:
            error = False
            for node in j.tools.develop.nodes.nodesGet():
                if node.selected==False:
                    continue    
                if error is False:
                    if changedfile.find("/.git/") != -1:
                        return
                    elif changedfile.find("/__pycache__/") != -1:
                        return
                    elif changedfile.endswith(".pyc"):
                        return
                    else:
                        destpart = changedfile.split("code/", 1)[-1]
                        dest = j.sal.fs.joinPaths(node.prefab.core.dir_paths['CODEDIR'], destpart)
                    e = ""
                    if action == "copy":
                        print("copy: %s %s:%s" % (changedfile, node, dest))
                        try:
                            node.ftpclient.put(changedfile, dest)
                        except Exception as e:
                            print("** ERROR IN COPY, WILL SYNC ALL")
                            error = True
                    elif action == "delete":
                        print("delete: %s %s:%s" % (changedfile, node, dest))
                        try:
                            node.ftpclient.remove(dest)
                        except Exception as e:
                            if "No such file" in str(e):
                                return
                            else:
                                error = True
                                # raise RuntimeError(e)
                    else:
                        raise j.exceptions.RuntimeError("action not understood in filesystemhandler on sync:%s"%action)

                if error:
                    try:
                        print(e)
                    except BaseException:
                        pass
                    node.sync()
                    error=False

    def on_moved(self, event):
        j.tools.develop.syncCode()
        self.handler(event, action="delete")

    def on_created(self, event):
        self.handler(event)

    def on_deleted(self, event):
        self.handler(event, action="delete")

    def on_modified(self, event):
        self.handler(event)
