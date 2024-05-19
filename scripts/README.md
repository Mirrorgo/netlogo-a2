# Project Structure
``` shell
.
├── README.md
├── extension1
│   ├── extension1.py # extension1 
│   ├── extension1_0.1.csv
│   ├── extension1_0.2.csv
│   ├── extension1_0.3.csv
│   ├── extension1_0.4.csv
│   ├── extension1_0.5.csv
│   ├── extension1_0.6.csv
│   ├── extension1_0.7.csv
│   ├── extension1_0.8.csv
│   ├── extension1_0.9.csv
│   ├── extension1_0.csv
│   └── extension1_1.csv
├── extension2
│   ├── extension2.py # extension2
│   └── extension2.py.csv
└── replication
    ├── origin.py # python: replication of netlogo model
    ├── origin.py.csv
    ├── rep1.nlogo # netlogo: experiment1 to verify our replication
    ├── rep1.nlogo.csv 
    ├── rep1.py # python: experiment to verify our replication
    ├── rep1.py.csv
    ├── rep2.nlogo # netlogo: experiment2 to verify our replication
    ├── rep2.nlogo.csv
    ├── rep2.py # python: experiment to verify our replication
    └── rep2.py.csv
```

# Setup Tutorial 
## replication
- run `python origin.py` and see the result in `origin.py.csv`
- To prove that we have successfully implement the model in python, run `python rep1.py` ,`python rep2.py` and you can clearly obeserve **"Salami Tactics of Corruption"** phenomenon in `rep1.py.csv` and `rep2.py.csv`
- We make some some chanegs in orginal model the observe the phenomenon. And the `rep1.nlogo` and `rep2.nlogo` are the netlogo files corresponding to the `rep1.py` and `rep2.py`.
- `rep1.nlogo.csv` and `rep2.nlogo.csv` are the result of `rep1.nlogo` and `rep2.nlogo`

## extension1
- run `python extension1.py` and see the result in the csv files in `extension1` folder

## extension2
- run `python extension2.py` and see the result in the csv files in `extension2` folder