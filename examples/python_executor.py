from crypto import Crypto
from pycolonies import colonies_client
from pycolonies import func_spec
from pycolonies import ColoniesConnectionError
import signal
import base64 
import os
import uuid
import sys

class PythonExecutor:
    def __init__(self):
        global colonies
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        crypto = Crypto()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey= colony_prvkey
        self.executor_prvkey = crypto.prvkey()
        self.executorid = crypto.id(self.executor_prvkey)
        self.executorname = "python-executor"
        self.executortype = "python-executor"

        self.register()
        
    def register(self):
        executor = {
            "executorname": self.executorname,
            "executorid": self.executorid,
            "colonyname": self.colonyname,
            "executortype": self.executortype
        }
        
        try:
            self.colonies.add_executor(executor, self.colony_prvkey)
            self.colonies.approve_executor(self.colonyname, self.executorname, self.colony_prvkey)
        except Exception as err:
            print(err)
            sys.exit(-1)
        
        print("Executor", self.executorname, "registered")
   
    def start(self):
        while (True):
            try:
                # try to get a process from the colonies server, the call will block for max 10 seconds
                # an exception will be raised if no processes can be assigned, and we will restart start the while loop
                assigned_process = self.colonies.assign(self.colonyname, 10, self.executor_prvkey)
                print()
                print("Process", assigned_process.processid, "is assigned to Executor")

                # ok, executor was assigned a process, extract the function code to run
                code_base64 = assigned_process.spec.env["code"]
                code_bytes2 = base64.b64decode(code_base64)
                code = code_bytes2.decode("ascii")

                # add the function to the global scope
                exec(code)

                # extract args and call the function code we just injected
                funcspec = assigned_process.spec
                funcname = funcspec.funcname
                try:
                    self.colonies.add_function(self.colonyname, 
                                             self.executorname, 
                                             funcname,  
                                             self.executor_prvkey)
                except Exception as err:
                    print(err)

                try:
                    # if "input" is defined, it is the output of the parent process,
                    # use the output from parent process instead of args
                    
                    if assigned_process.input is not None and len(assigned_process.input)>0:
                        args = assigned_process.input
                    else:
                        args = funcspec.args
                except Exception as err:
                    print(err)

                print("Executing:", funcspec.funcname)

                # call the injected function
                try:
                    ctx = {"process": assigned_process,
                           "colonyname": self.colonyname,
                           "executorid": self.executorid,
                           "executor_prvkey": self.executor_prvkey}
                      
                    res = eval(funcname)(*tuple(args), ctx=ctx)

                    if res is not None:
                        if type(res) is tuple:
                            res_arr = list(res)
                        else:
                            res_arr = [res]
                    else:
                        res_arr = []
                except Exception as err:
                    print("Failed to execute function:", err)
                    self.colonies.fail(assigned_process.processid, ["Failed to execute function"], self.executor_prvkey)
                    continue

                print("done")
                # close the process as successful
                self.colonies.close(assigned_process.processid, res_arr, self.executor_prvkey)
            except ColoniesConnectionError as err:
                print(err)
                sys.exit(-1)
            except Exception as err:
                pass

    def unregister(self):
        self.colonies.remove_executor(self.colonyname, self.executorname, self.colony_prvkey)
        print("Executor", self.executorname, "unregistered")
        os._exit(0)

def sigint_handler(signum, frame):
    executor.unregister()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    executor = PythonExecutor()
    executor.start()
