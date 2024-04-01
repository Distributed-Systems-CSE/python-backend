## TODO

- [x]  Load localchain
- [x]  Add block
- [x]  Listen to gossip
- [x]  Add peers (peers are taken from os.env)
- [x]  Send self Node object as pkl (so other nodes can verify the localchain)
- [ ]  Merge chains (This is invoked when)
  - [x]  A goosip is noticed
  - [ ]  Sync ledger is invoked 

## Prereq

```
pip install -r requirements.txt
```  

## Commands

1. Run individual flask app  
```
flask run --host 0.0.0.0 --port 5001
```  
2. Run dockerized flask apps  
```
docker-compose up --build
```  

1. Remove dangling images  
```
docker image prune
```  