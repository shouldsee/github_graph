GH_TOKEN=${1:-$GH_TOKEN}
docker build -t github_graph . &&\
 docker run -p 80:80 -e GH_TOKEN="$GH_TOKEN" --attach STDERR github_graph