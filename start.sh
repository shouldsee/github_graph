GH_TOKEN=${1:-$GH_TOKEN}
docker build -t github_graph . &&\
 docker run --network host -e GH_TOKEN="$GH_TOKEN" --attach STDERR github_graph
