# graph -> benchmark -> args
arg_dict = {
    'roadU.sg': {
        'tc' : '',
    },
    'road.sg': {
        'bfs': '',
        'pr' : '-i1000 -t1e-4',
        'cc' : '',
        'bc' : '-i4',
    },
    'road.wsg': {
        'sssp': '-d50000',
    },
}

run_dict = {
    'test': {
        'tc'  : 1,
        'bfs' : 1,
        'pr'  : 1,
        'cc'  : 1,
        'bc'  : 1,
        'sssp': 1,
    },
    'ref': {
        'tc'  : 3,
        'bfs' : 64,
        'pr'  : 16,
        'cc'  : 16,
        'bc'  : 16,
        'sssp': 64,
    },
}
