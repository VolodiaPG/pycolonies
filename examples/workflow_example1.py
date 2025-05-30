from pycolonies import colonies_client
from pycolonies import func_spec
from pycolonies import Workflow

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

def gen_nums(ctx={}):
    return 1, 2 

def sum_nums(n1, n2, ctx={}):
    return n1 + n2 

wf = Workflow(colonyname=colonyname)
f = func_spec(func=gen_nums,
              args=[], 
              colonyname=colonyname, 
              executortype="python-executor",
              priority=200,
              maxexectime=100,
              maxretries=3,
              maxwaittime=100)

wf.functionspecs.append(f)

f = func_spec(func=sum_nums, 
              args=[], 
              colonyname=colonyname, 
              executortype="python-executor",
              priority=200,
              maxexectime=100,
              maxretries=3,
              maxwaittime=100)

f.conditions.dependencies.append("gen_nums")

wf.functionspecs.append(f)

processgraph = colonies.submit_workflow(wf, prvkey)
print("Workflow", processgraph.processgraphid, "submitted")

# wait for the sum_list process
process = colonies.find_process("sum_nums", processgraph.processids, prvkey)
process = colonies.wait(process, 100, prvkey)
print(process.output[0])
