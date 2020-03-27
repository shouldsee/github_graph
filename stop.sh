docker stop $(docker ps|grep github_graph|cut -d' ' -f1)
