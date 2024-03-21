from pycolonies import colonies_client
from pycolonies import func_spec

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

f = func_spec(func="echo", 
              args=["helloworld"], 
              colonyname=colonyname, 
              executortype="echo-executor",
              priority=200,
              maxexectime=100,
              maxretries=3,
              maxwaittime=100)

process = colonies.submit_func_spec(f, prvkey)
print("Process", process.processid, "submitted")
process = colonies.wait(process, 100, prvkey)
print(process.output[0])

