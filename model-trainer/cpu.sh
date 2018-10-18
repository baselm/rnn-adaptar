#!/bin/bash
docker-machine create --driver google --google-project selfhealing-216620 \
--google-zone europe-west2-b   --google-machine-type n1-standard-1 --google-disk-size 10 swarm-7
eval $(docker-machine env swarm-1)
TOKEN=$(docker swarm join-token -q worker)

eval $(docker-machine env swarm-10)

docker swarm join --advertise-addr $(docker-machine ip swarm-10) \
        --token $TOKEN $(docker-machine ip swarm-1):2377
eval $(docker-machine env swarm-1)
docker node ls
