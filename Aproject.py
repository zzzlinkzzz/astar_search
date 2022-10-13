import streamlit as st
from pyvis.network import Network
import json
import streamlit.components.v1 as components

red = "#FF3008"
blue = "#2b7ce9"
green = "#97c2fc"
back = "#1f1f21"
pink = "#DED007"

# data
def get_data(filename):
    with open(f'data/{filename}.json', "r") as file:
        data = json.load(file)
        return data

coor = get_data('coor')
link = get_data('network')

pos = {key: [int(round(coor[key][0]-51.5,5)*10**5),int(round(coor[key][1],5)*10**5)] for key in coor.keys()}

# base map
def map_algs(g, alg="barnes"):
    if alg == "barnes":
        g.barnes_hut()
    if alg == "forced":
        g.force_atlas_2based()
    if alg == "hr":
        g.hrepulsion()

g = Network(height = '600px', width = "100%", bgcolor = "#222222", font_color="White")
for node in pos.keys():
    x = pos[node][0]
    y = pos[node][1]
    n = len(link[node])
    if n < 4:
        color = green
        size = 20
    elif n < 7:
        color = pink
        size = 30
    else:
        color = red
        size = 50
    g.add_node(node, color = color, shape = "dot",size = size, label = node, x = x/1.5 , y = -y/4.5,labelHighlightBold = True)

for node in link.keys():
    if len(link[node]) > 6:
        for sub_node in link[node]:
             g.add_edge(node,sub_node,color = red, width  = 5, physics = False) 
    else:
        for sub_node in link[node]:
             g.add_edge(node,sub_node,color = blue, width  = 4, physics = False)

map_algs(g, alg="hr")
g.save_graph('temp/temp.html')

# draw route
def solve(start_node, end_node, coor, link, max_search_node = 2):
    def norm1(start, end, coor):
        x1 = coor[start][0]
        x2 = coor[end][0]
        y1 = coor[start][1]
        y2 = coor[end][1]
        return abs(x1 - x2) + abs(y1 - y2)

    start_node = [start_node]
    end_node = end_node

    visited = set()
    def AStarSearch(start_node, end_node, coor, link, max_search_node = 3):
        cost = []
        candidate = []
        nonlocal visited
        for node in start_node:
            for sub_node in link[node]:
                cost.append([node, sub_node, norm1(node, sub_node, coor) + norm1(sub_node, end_node, coor)]) # g + h
        cost = [x for x in cost if x[1] not in visited]
        if len(cost) == 0:
            candidate.extend(['','',1])
            return candidate
        temp = sorted(cost, key = lambda x: x[2])
        temp = temp[:min(max_search_node,len(temp))]
        nearest_nodes = [x[1] for x in temp]
        for x  in nearest_nodes: visited.add(x)
        if end_node not in nearest_nodes:
            candidate.extend(temp)
            candidate.extend(AStarSearch(nearest_nodes, end_node, coor, link))
        else:
            candidate.extend(temp)
        return candidate
    
    potential = []
    def find_path(start_node, end_node, candidate):
        path = []
        temp = [x for x in candidate if x[1] == end_node]
        for elem in temp:
            if elem[0] not in potential:
                potential.append(elem[0])
                if elem[1] != start_node[0]:
                    path.append(elem)
                    path.extend(find_path(start_node, elem[0],  candidate))
                else:
                    path.append(elem)
    
        return path
    candidate = AStarSearch(start_node, end_node, coor, link)
    path = find_path(start_node, end_node,  candidate)[::-1]
    path = list(list(zip(*path))[0]) +  [end_node]
    path = path[path.index(start_node[0]):]
    return path, candidate, visited


def draw_route(path, candidate, visited):
    candidate = list(list(zip(*candidate)))
    candidate = set(candidate[0]).union(set(candidate[1]))
    r = Network(height = '600px', width = "100%", bgcolor = "#222222", font_color="White")
    for node in pos.keys():
        x = pos[node][0]
        y = pos[node][1]
        if node in path:
            color = red
            size = 60
            shape = "dot"
        elif node in visited:
            color = pink
            size = 40
            shape = "dot"
        else:
            color = green
            size = 20
            shape = "dot"
        r.add_node(node, color = color, shape = shape,size = size, label = node, x = x/1.5 , y = -y/4.5, labelHighlightBold = True )
    for node in link.keys():
        for sub_node in link[node]:
            if sub_node in path:
                continue
            r.add_edge(node,sub_node, color = blue, width  = 4, physics = False)     
    for i in range(len(path)-1):
        r.add_edge(path[i], path[i+1], color = red, width  = 10, physics = False)
    map_algs(r, alg="hr")
    r.save_graph('temp/route.html')






# UI
gare_list = sorted(list(coor.keys()))

st.sidebar.title("Sơ đồ đường tàu:")
base_network = st.sidebar.button("Hiện")

st.sidebar.title("Định tuyến:")
departure = st.sidebar.selectbox("Điểm đi:",gare_list)
destination = st.sidebar.selectbox("Điểm đến:",gare_list)
route = st.sidebar.button("Tìm đường")

st.title("Thuật toán A* tìm đường đi giữa 2 điểm")
st.header("Ứng dụng trên hệ thống tàu điện ngầm London")

if base_network:
    HtmlFile = open('temp/temp.html', 'r',  encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height = 1000, width = 1000)

if route:
    path, candidate, visited = solve(departure, destination, coor, link, max_search_node = 3)
    draw_route(path, candidate, visited)
    HtmlFile = open('temp/route.html', 'r',  encoding='utf-8')
    source_code = HtmlFile.read()
    st.header("Route:")
    st.write(" > ".join(path))
    components.html(source_code, height = 1000, width = 1000)
