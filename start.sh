GH_TOKEN=${1:-$GH_TOKEN}
false && {
docker build -t github_graph . &&\
 docker run --network host -e GH_TOKEN="$GH_TOKEN" --attach STDERR github_graph
}
uvicorn --port 10010 main:app --reload

