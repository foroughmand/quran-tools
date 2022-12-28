from dataclasses import dataclass
from quran import Quran, Token
# from flask import Flask
# from flask_restful import Resource, Api
# from flask_restful import reqparse
# from flask import Flask, jsonify, request
import json

@dataclass
class Range:
    sindex: int
    aindex_begin: int
    aindex_end: int


def common_roots(quran: Quran, ranges: list[Range], min_nonpresent_cnt: int = 0, root_type: int = 0, ret_instances: bool = False):
    def root_extractor_root(t: Token):
        return t.root()
    def root_extractor_lem(t: Token):
        return t.lem()
    root_extractor = root_extractor_root if root_type == 0 else root_extractor_lem

    rf_all, rf_instances_all = [], []
    common_roots = {}
    for range in ranges:
        rf, rf_instances = {}, {}
        for a in quran[range.sindex].range(range.aindex_begin, range.aindex_end):
            for t in a.items():
                root = root_extractor(t)
                if root is not None:
                    if root not in rf: rf[root], rf_instances[root] = 0, []
                    rf[root] += 1
                    if ret_instances:
                        rf_instances[root].append(t.loc())
        for r, f in rf.items():
            if r not in common_roots: common_roots[r] = 0
            common_roots[r] += 1
        rf_all.append(rf)
        rf_instances_all.append(rf_instances)
    rf_instances_all = [{r:instances for (r, f), (r2, instances) in zip(rf.items(), rf_instances.items()) if len(ranges) - common_roots[r] <= min_nonpresent_cnt} for rf, rf_instances in zip(rf_all, rf_instances_all)]
    rf_all = [{r:f for r, f in rf.items() if len(ranges) - common_roots[r] <= min_nonpresent_cnt} for rf in rf_all]
    # print('common_roots', rf_instances_all)
    return rf_all, rf_instances_all

# app = Flask(__name__)
# api = Api(app)
# 
# @app.route('/common_roots/ranges=<string:data_string>&min_nonpresent_cnt=<int:min_nonpresent_cnt>')
# def common_roots_get(data_string: str, min_nonpresent_cnt: int):
#     # print(data_string)
#     data = json.loads(data_string)
#     # print(data)
#     # return {'a': 'b'}
#     # return request.get_json()
#     quran = Quran()
#     ret = []
#     for rf, range in zip(common_roots(quran, [Range(r[0], r[1], r[2]) for r in data], min_nonpresent_cnt), data):
#         ret.append({'rf': rf, 'range': range})

#     return json.dumps(ret, ensure_ascii=False).encode('utf8')

# if __name__ == '__main__':
#     app.run(debug=True)

    
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "*://foroughmand.ir",
    "*://*.foroughmand.ir",
    "*://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/common_roots/ranges={data_string}&min_nonpresent_cnt={min_nonpresent_cnt}&root_type={root_type}&ret_instances={ret_instances}')
def read_item(data_string: str, min_nonpresent_cnt: int, root_type: int, ret_instances: bool):
    data = json.loads(data_string)
    quran = Quran()
    ret = []
    for rf, rf_instances, range in zip(*common_roots(quran, [Range(r[0], r[1], r[2]) for r in data], min_nonpresent_cnt, root_type, ret_instances), data):
        # print('read_item', rf, rf_instances, range)
        ret.append({'rf': rf, 'range': range, 'instances': {r:list(instances) for r, instances in rf_instances.items()}})
    
    # print(data)

    # return json.dumps(ret, ensure_ascii=False).encode('utf8')
    # return {"data_string": data_string, "min_nonpresent_cnt": min_nonpresent_cnt}
    return ret
