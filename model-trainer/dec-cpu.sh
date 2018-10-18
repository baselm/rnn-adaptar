#!/bin/bash
docker-machine rm -f swarm-7
eval $(docker-machine env swarm-1)
docker node ls
