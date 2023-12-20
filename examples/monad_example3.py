import sys
sys.path.append(".")
from pycolonies import colonies_client
from colonies_monad import ColoniesMonad
from colonies_monad import Function

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

def gen_data(ctx={}):
    return 1, 2 

def process_data(*nums, ctx={}):
    total = 0
    for n in nums:
        total += n
    return total 

def print_result(total, ctx={}):
    print("total=", total)
    return total

gen_data_fn = Function(gen_data, colonyname, executortype="python-executor")
process_data_fn = Function(process_data, colonyname, executortype="python-executor")
print_fn = Function(print_result, colonyname, executortype="python-executor")

m = ColoniesMonad(colonies, colonyname, prvkey)
(m >> gen_data_fn >>  process_data_fn >> print_fn).unwrap()
