token=${1:-$token}
repo_acc=${2:-cancerit/cgpBigWig}
set -ue
# starred_param
cat <<EOF >temp.gql
query { 
	user(login:"shouldsee") { 
		login
		starredRepositories(last:2) { 
			nodes { 
				name 
				url
				stargazers(last:80){
					nodes {
						login
						starredRepositories(last:10) {
							nodes {
								name
								url
							}
						}
					}
				}
			} 
		}
	}
}
EOF

cat <<EOF >temp.gql
query { 
	user(login:"shouldsee") { 
		login
		starredRepositories(last:2) { 
			nodes { 
				name 
				url
				stargazers(last:80){
					nodes {
						login
						starredRepositories(last:10) {
							nodes {
								name
								url
							}
						}
					}
				}
			} 
		}
	}
}
EOF
#hasura/graphqurl

# CSSEGISandData/COVID-19

# curl https://api.github.com/graphql -H "Authorization: bearer $token" -X POST -d "{"data":$(cat temp.sql)}"
# exit 0

# gq https://api.github.com/graphql -H "Authorization: bearer $token" \
# --queryFile temp.gql >temp.json


python3 -<<EOF 
# import sys; sys.exit(0)
# > temp.py

from gql import Client,gql
from gql.transport.requests import RequestsHTTPTransport

sample_transport=RequestsHTTPTransport(
    url='https://api.github.com/graphql',
    use_json=True,
    headers={
    	"Authorization": "bearer $token",
        "Content-type": "application/json",
    },
    verify=False
)

client = Client(
    retries=3,
    transport=sample_transport,
    fetch_schema_from_transport=True,
)



from jinja2 import Template,StrictUndefined

# owner = "hasura"
repo_query = '''owner:"hasura" name:"graphqurl"'''
repo_query = '''owner:"hasura" name:"graphqurl"'''

def jinja2_format(s,**kw):
	ss = Template(s,undefined=StrictUndefined).render(**kw)
	return ss

repo_acc = '$repo_acc'
# repo_acc = 'cancerit/cgpBigWig'
# repo_acc = 'DataBiosphere/toil'
# repo_acc = 'snakemake/snakemake'
# repo_acc = 'broadinstitute/cromwell'
# repo_acc = 'CSSEGISandData/COVID-19'
owner, name = repo_acc.split('/')
repo_query = jinja2_format('''owner:"{{owner}}" name:"{{name}}"''',**locals())


s = '''
query{
	repository({{repo_query}} )
	{ 
					name 
					url
					stargazers(last:100){
						nodes {
							login
							starredRepositories(last:50) {
								nodes {
									name
									url
								}
							}
						}
					}
				}
			}
'''
query = gql(
Template(s,undefined=StrictUndefined).render(**locals())
)


### hasura/graphqurl

res = client.execute(query)

import json
with open('temp.json','w') as f:
	json.dump(dict(data=res),f)
EOF

python3 -<<EOF
import sys,os,json
from pprint import pprint

def get_nodes():
	fn = 'temp.json'
	with open(fn,'r') as f:
		d0 = d = json.load(f)
	nodes = [d['data']['repository']]

	# nodes = d['data']['user']['starredRepositories']["nodes"]
	return nodes

nodes = get_nodes()
edges = []
for n in nodes:
	for sg in n["stargazers"]["nodes"]:
		for n2 in sg["starredRepositories"]["nodes"]:
			if n["url"]!=n2["url"]:
				edges.append((n["url"],sg["login"],n2["url"]))
print(len(edges))	
from collections import Counter
ct = Counter([(x[0],x[-1]) for x in edges])

pprint(ct.most_common(10))

from graphviz import Digraph,Graph
from graphviz import escape,nohtml


# g = Graph('G',strict=True,engine="neato",graph_attr=dict(nodesep="1."))
# g.attr(overlap="scalexy")
# # g.attr(overlap="compress")
# # g.attr(overlap="false")
# g.attr(overlap="ipsep")
# g.attr(sep="0.1")
# g.attr(nodesep='1.')
# # g.attr(sep="+1")
# # g.attr(sep="+1")

g = Graph('G',strict=True,engine="dot")
# g.attr(rankdir='TB')
g.attr(rankdir='LR')


def _label(x):
    # x = r'\l'.join(textwrap.wrap(repr(x),width=50)) 
    # x = x.replace(':','_')
    # x = x.replace(':','_')
    x = x.split('://',1)[-1]
    return x 

def is_included(n1,sg,n2):
	return (ct[(n1,n2)] >=3)
_inced = [tuple(x[0]) for x in ct.most_common(10) ]
def is_included(n1,sg,n2):
	return tuple((n1,n2)) in _inced

if 1:
	i = -1
	for n1,sg,n2 in edges:
		if not is_included(n1,sg,n2):
			continue

		i+= 1
		# user = str(i)
		# user = "%04d_%s"%(i,sg)
		user = "github.com/%s"%sg
		# user = sg
		g.edge(_label(n1),user)
		g.edge(user,_label(n2))

		g.node(_label(n1), href=n1)
		g.node(_label(n2), href=n2)
		g.node(user, href="https://github.com/%s"%sg)


else:
	for (n1,n2),ct in ct.most_common():
		# if ct >= 3:
		if ct >= 3:
			g.edge(_label(n1),_label(n2),weight=str(ct))
g.render('temp.dot.txt',format='svg')
EOF
# rm temp.dot*
echo done