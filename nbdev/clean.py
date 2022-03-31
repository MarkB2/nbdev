# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_clean.ipynb (unless otherwise specified).

__all__ = ['rm_execution_count', 'clean_output_data_vnd', 'colab_json', 'clean_cell_output', 'cell_metadata_keep',
           'nb_metadata_keep', 'clean_cell', 'clean_nb', 'nbdev_clean_nbs']

# Cell
import io,sys,json,glob,re
from fastcore.script import call_parse,Param,bool_arg
from fastcore.utils import ifnone
from .imports import Config
from .export import nbglob
from pathlib import Path

# Cell
def rm_execution_count(o):
    "Remove execution count in `o`"
    if 'execution_count' in o: o['execution_count'] = None

# Cell
colab_json = "application/vnd.google.colaboratory.intrinsic+json"
def clean_output_data_vnd(o):
    "Remove `application/vnd.google.colaboratory.intrinsic+json` in data entries"
    if 'data' in o:
        data = o['data']
        if colab_json in data:
            new_data = {k:v for k,v in data.items() if k != colab_json}
            o['data'] = new_data

# Cell
def clean_cell_output(cell):
    "Remove execution count in `cell`"
    if 'outputs' in cell:
        for o in cell['outputs']:
            rm_execution_count(o)
            clean_output_data_vnd(o)
            o.get('metadata', o).pop('tags', None)

# Cell
cell_metadata_keep = ["hide_input"]
nb_metadata_keep   = ["kernelspec", "jekyll", "jupytext", "doc"]

# Cell
def clean_cell(cell, clear_all=False):
    "Clean `cell` by removing superfluous metadata or everything except the input if `clear_all`"
    rm_execution_count(cell)
    if 'outputs' in cell:
        if clear_all: cell['outputs'] = []
        else:         clean_cell_output(cell)
    if cell['source'] == ['']: cell['source'] = []
    cell['metadata'] = {} if clear_all else {k:v for k,v in cell['metadata'].items() if k in cell_metadata_keep}

# Cell
def clean_nb(nb, clear_all=False):
    "Clean `nb` from superfluous metadata, passing `clear_all` to `clean_cell`"
    for c in nb['cells']: clean_cell(c, clear_all=clear_all)
    nb['metadata'] = {k:v for k,v in nb['metadata'].items() if k in nb_metadata_keep }

# Cell
def _print_output(nb):
    "Print `nb` in stdout for git things"
    _output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    x = json.dumps(nb, sort_keys=True, indent=1, ensure_ascii=False)
    _output_stream.write(x)
    _output_stream.write("\n")
    _output_stream.flush()

# Cell
@call_parse
def nbdev_clean_nbs(
    fname:str=None,  # A notebook name or glob to convert
    clear_all:bool_arg=False,  # Clean all metadata and outputs
    disp:bool_arg=False,  # Print the cleaned outputs
    read_input_stream:bool_arg=False  # Read input stram and not nb folder
):
    "Clean all notebooks in `fname` to avoid merge conflicts"
    #Git hooks will pass the notebooks in the stdin
    if read_input_stream and sys.stdin:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        nb = json.load(input_stream)
        clean_nb(nb, clear_all=clear_all)
        _print_output(nb)
        return
    path = None
    if fname is None:
        try: path = get_config().path("nbs_path")
        except Exception as e: path = Path.cwd()

    files = nbglob(fname=ifnone(fname,path))
    for f in files:
        if not str(f).endswith('.ipynb'): continue
        nb = json.loads(open(f, 'r', encoding='utf-8').read())
        clean_nb(nb, clear_all=clear_all)
        if disp: _print_output(nb)
        else:
            x = json.dumps(nb, sort_keys=True, indent=1, ensure_ascii=False)
            with io.open(f, 'w', encoding='utf-8') as f:
                f.write(x)
                f.write("\n")
