from dataclasses import dataclass
from quran import Quran
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


def common_roots(quran: Quran, ranges: list[Range], min_nonpresent_cnt: int = 0):
    rf_all = []
    common_roots = {}
    for range in ranges:
        rf = {}
        for a in quran[range.sindex].range(range.aindex_begin, range.aindex_end):
            for t in a.items():
                if t.root() is not None:
                    if t.root() not in rf: rf[t.root()] = 0
                    rf[t.root()] += 1
        for r, f in rf.items():
            if r not in common_roots: common_roots[r] = 0
            common_roots[r] += 1
        rf_all.append(rf)
    rf_all = [{r:f for r, f in rf.items() if len(ranges) - common_roots[r] <= min_nonpresent_cnt} for rf in rf_all]
    return rf_all

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

app = FastAPI()

@app.get('/common_roots/ranges={data_string}&min_nonpresent_cnt={min_nonpresent_cnt}')
def read_item(data_string: str, min_nonpresent_cnt: int):
    data = json.loads(data_string)
    quran = Quran()
    ret = []
    for rf, range in zip(common_roots(quran, [Range(r[0], r[1], r[2]) for r in data], min_nonpresent_cnt), data):
        ret.append({'rf': rf, 'range': range})
    
    print(data)

    # return json.dumps(ret, ensure_ascii=False).encode('utf8')
    # return {"data_string": data_string, "min_nonpresent_cnt": min_nonpresent_cnt}
    return ret
