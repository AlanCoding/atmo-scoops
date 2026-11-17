"""JSON summaries and losslessly compressed trajectory storage."""
import gzip
import json
from pathlib import Path


def read_result(path):
    path=Path(path)
    if not path.exists() and path.suffix=='.json':path=path.with_suffix('.json.gz')
    if path.suffix=='.gz':
        with gzip.open(path,'rt') as stream:return json.load(stream)
    return json.loads(path.read_text())


def write_trajectory(path,result):
    path=Path(path)
    if path.suffix!='.gz':path=path.with_suffix(path.suffix+'.gz')
    with gzip.open(path,'wt',compresslevel=6) as stream:json.dump(result,stream,allow_nan=False)
    return path
