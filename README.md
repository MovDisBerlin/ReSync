# ReSync

## About
ReSync is an open-access tool to align intracerebral recordings (from DBS electrodes) with external recordings. A manuscript describing ReSync's functionality and methodology will follow.

This repo is structured as follows: 

```
.
├── results
├── scripts
│   ├── functions
│   │   ├── find_artifacts
│   │   ├── interactive
│   │   ├── loading_data
│   │   ├── packet_loss
│   │   ├── plotting
│   │   ├── resync_function
│   │   ├── timeshift
│   │   ├── tmsi_poly5reader
│   │   └── utils    
│   ├── main_batch
│   └── main
├── sourcedata
│   └── recording_information.xlsx
├── environment.yml
├── LICENSE.txt
├── README.md
└── setup.py
```

```environment.yml``` contains all the packages and their version needed to run the ReSync algorithm.
```main``` and ```main_batch``` are the two main scripts that can be used to synchronize recordings:
* ```main``` is used to synchronize only two recordings from one session.
* ```main_batch``` can be used to automatize the synchronization of multiple sessions. To use ```main_batch```, the file recording_information.xlsx present in the sourcedata folder must be completed beforehand.

```sourcedata``` contains 2 example datasets to try the toolbox and have a look at the output: each dataset contains one intracerebral channel and one external channel, both with stimulation artifacts. NOTE: These example datasets were generated and saved as .csv files. Expected datasets from real recordings are usually .mat for intracerebral recordings and .Poly5 for external recordings. 
To obtain these formats:
* we record our external datas with a TMSi SAGA data recorder, from which the output file is either a .Poly5 or .xdf file
* we preprocess the .json files obtained after streaming from intracerebral DBS electrodes to obtain FieldTrip .mat files. To do so, there are two possibilities:
    - the open source “Perceive” toolbox (https://github.com/neuromodulation/perceive) for MATLAB
    - the open source "DBScope" toolbox (https://github.com/NCN-Lab/DBScope) for MATLAB

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. 

#### Repository
* GUI: use a git-manager of preference, and clone: https://github.com/juliettevivien/ReSync.git
* Command line:
    - set working directory to desired folder and run: ```git clone https://github.com/juliettevivien/ReSync.git```
    - to check initiated remote-repo link, and current branch: ```cd ReSync```, ```git init```, ```git remote -v```, ```git branch``` (switch to branch main e.g. with git checkout main)

#### Environment
* Anaconda prompt: you can easily install the required environment from your Anaconda prompt:
    - navigate to repo directory, e.g.: ```cd Users/USERNAME/Research/ReSync```
    - ```conda env create –f environment.yml``` (Confirm Proceed? with ```y```)
    - ```conda activate resync```
    - ```git init```
 
* If for some reason this method is not working, try these lines in the Anaconda Prompt (it can happen for Mac users):
    - navigate to repo directory, e.g.: ```cd Users/USERNAME/Research/ReSync```
    - ```conda create --name resync python==3.10.9 pandas==1.5.3 scipy==1.10.0 numpy==1.23.5 openpyxl==3.0.10 jupyter==1.0.0```
    - ```conda activate resync```
    - ```pip install mne==1.3.0 pymatreader matplotlib==3.6.3 pybv```


## User Instructions:

* Make sure your environment has the required packages installed, either manually, or by following the instructions above.
* ReSync can be executed directly from the main.py or main_batch.py files.


## Authors

* **Juliette Vivien** - *Initial work* -

*  **Alessia Cavallo** - *Contributor/Code review* 

* **Jeroen Habets** - *Contributor* - https://github.com/jgvhabets

## Questions or contributions
Please don't hesitate to reach out if any questions or suggestions! @ juliette.vivien@charite.de  or https://twitter.com/vivien_juliette


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

