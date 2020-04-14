# from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, APIRouter
# from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse, Response
import requests
from fastapi.openapi.utils import get_openapi

def read_close(fn,encoding=None):
	with open(fn,"rb") as f:
		return f.read().decode(encoding) if encoding else f.read().decode()

# resp = requests.get("http://newflaw.com")
if 1:
	PREFIX='/github_graph'
	app = FastAPI(
		openapi_url=PREFIX+"/openapi.json",
		docs_url=PREFIX+"/docs",
		)
	# app.mount(PREFIX+"/static", StaticFiles(directory="."), name="static");
	router = APIRouter()
	def custom_openapi(PREFIX=PREFIX):
	    if app.openapi_schema:
	        return app.openapi_schema
	    openapi_schema = get_openapi(
	    	title = "github_graph",
	        # title="Custom title",
	        version=read_close("VERSION").strip(),
	        description=jinja2_format('''

<img width="16" height="16" src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"></img>[Github](https://github.com/shouldsee/github_graph)

This project aims to provide an  API for browsing github.


	 ''',**locals()),
	        routes=app.routes,
	    )
	    openapi_schema["info"]["x-logo"] = {
	        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
	    }
	    app.openapi_schema = openapi_schema
	    return app.openapi_schema
	app.openapi = custom_openapi


if 1:
	# @app.get("/blog/{url:path}")
	# def get_blog(url):
	# 	# resp = 
	# 	resp = requests.get("http://localhost:9000/%s"%url)
	# 	resp = Response(
	# 		content=resp.content,
	# 		status_code = resp.status_code,
	# 		headers = resp.headers,
	# 		media_type=resp.headers.get('Content-Type', '')
	# 		)
	# 	return resp



	@router.get("/")
	def read_root():
		# return RedirectResponse('/blog')
		return RedirectResponse(PREFIX+'/docs')
	    # return {"Hello": "World"}

	@router.get("/repo/{owner}/{name}", response_class = HTMLResponse)
	def show_repo_graph(owner: str, name: str):
		import time
		t0 = time.time()
		nodes = query_repo_graph(owner, name)
		svg = render_graph( nodes)
		dt = time.time() - t0
		dt = "%.3f"%dt

		temp = '''
		<html>
		<body>
		<p>
		Runtime: {{dt}}s
		</p>
		<p>
		Root: Repo: {{owner}}/{{name}}
		</p>
		{{svg}}
		</body>
		</html>'''
		s = jinja2_format(temp,**locals())
		return s


	from gql import Client,gql
	from gql.transport.requests import RequestsHTTPTransport
	from jinja2 import Template,StrictUndefined
	def jinja2_format(s,**kw):
		ss = Template(s,undefined=StrictUndefined).render(**kw)
		return ss

	import sys
	def _stderrline(s):
		sys.stdout.write(s+'\n')
		sys.stderr.write(s+'\n')

	def get_gh_token():
		import os
		token = os.environ.get('GH_TOKEN', '')
		if not token:
			raise HTTPException(status_code=404, detail="GH_TOKEN not found")
		return token

	import cachetools.func
	@cachetools.func.ttl_cache(maxsize=128, ttl=600, typed=False)	
	def query_repo_graph( owner, name):
		# token = '$token'
		# repo_acc = '$repo_acc'
		# owner, name = repo_acc.split('/')
		_stderrline('[DBG] Getting %s,%s'%(owner,name))
		token = get_gh_token()
		repo_query = jinja2_format('''owner:"{{owner}}" name:"{{name}}"''',**locals())
		# repo_query = '''owner:"hasura" name:"graphqurl"'''

		sample_transport=RequestsHTTPTransport(
		    url='https://api.github.com/graphql',
		    use_json=True,
		    headers={
		    	"Authorization": jinja2_format("bearer {{token}}",**locals()),
		        "Content-type": "application/json",
		    },
		    verify=False
		)

		client = Client(
		    retries=3,
		    transport=sample_transport,
		    fetch_schema_from_transport=True,
		)


		s = '''
	query{
		repository({{repo_query}} )
		{ 
						name 
						url
						stargazers(last:50){
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
		s = Template(s,undefined=StrictUndefined).render(**locals())

		# _stderrline(s)
		query = gql(s)
		res = client.execute(query)
		return [ res['repository'] ]




		# def get_nodes():
		# 	fn = 'temp.json'
		# 	with open(fn,'r') as f:
		# 		d0 = d = json.load(f)
		# 	nodes = [d['data']['repository']]
		# 	# nodes = d['data']['user']['starredRepositories']["nodes"]
		# 	return nodes
		# nodes = get_nodes()
	def render_graph(nodes):
		import sys,os,json
		from pprint import pprint

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


		#### control graph layout
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
			n1 = nodes[0]['url']
			g.node(_label(n1),href=n1)

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
		with open('temp.dot.txt.svg','r') as f: svg = f.read()
		return svg

app.include_router(router,prefix=PREFIX)
