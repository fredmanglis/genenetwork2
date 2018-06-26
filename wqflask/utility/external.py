# Call external program

import os
import sys
import subprocess

def shell(command):
    if subprocess.call(command, shell=True) != 0:
        raise Exception("ERROR: failed on "+command)

def shell_with_return(cmd_list):
    results = subprocess.run(cmd_list, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    the_error = results.stderr.decode("utf-8")
    if(the_error):
        raise RuntimeError("shell_with_return failed with {}".format(the_error))

    return results.stdout.decode("utf-8")

def run_with_python2(cmd_args):
    from . import tools
    py_list = ["env", "PYTHONPATH={}".format(tools.PYTHON2_PATH),
                tools.PYTHON2_PROFILE+"/bin/python", "-m"]
    return shell_with_return(py_list + cmd_args)
    
