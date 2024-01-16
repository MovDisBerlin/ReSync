# ReSync

## About
ReSync is an open-access tool to align intracerebral recordings (from DBS electrodes) with external recordings. A manuscript describing ReSync's functionality and methodology will follow.

This repo is structured as follows: 

```
.
├── results
├── scripts
│   ├── find_artefacts
│   ├── interactive
│   ├── loading_data
│   ├── main_batch
│   ├── main_resync
│   ├── main
│   ├── packet_loss
│   ├── plotting
│   ├── sync
│   ├── timeshift
│   ├── tmsi_poly5reader
│   └── utils
├── sourcedata
    └── recording_information.xlsx
├── environment.yml
├── LICENSE.txt
├── README.md
└── setup.py


```
```environment.yml`` contains all the packages and their version needed to run the ReSync algorithm.
```main``` and ```main_batch``` are the two main scripts that can be used to synchronize recordings.
```main``` is used to synchronize only two recordings from one session. 
```main_batch``` can be used to automatize the synchronization of multiple sessions. To use ```main_batch```, the file recording_information.xlsx present in the sourcedata folder must be completed previously.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. 

#### Repository
* GUI: use a git-manager of preference, and clone: https://github.com/juliettevivien/ReSync.git
* Command line:
    - set working directory to desired folder and run: ```git clone https://github.com/juliettevivien/ReSync.git```
    - to check initiated remote-repo link, and current branch: ```cd ReSync```, ```git init```, ```git remote -v```, ```git branch``` (switch to branch main e.g. with git checkout main)

#### Environment
* GUI: Create a python environment with the correct requirements. Either use the GUI of a environments-manager (such as anaconda), and install all dependencies mentioned in the env_requirements.txt.
* Anaconda prompt: you can easily install the required environment from your Anaconda prompt:
    - navigate to repo directory, e.g.: ```cd Users/USERNAME/Research/ReSync```
    - ```conda env create –f environment.yml``` (Confirm Proceed? with ```y```)
    - ```conda activate resync```
    - ```git init```


## User Instructions:

* Make sure your environment has the required packages installed, either manually, or by following the instructions above.
* ReSync can be executed directly from the main.py or main_batch.py files.


## Authors

* **Juliette Vivien** - *Initial work* -

* **Jeroen Habets** - *Contributor* - https://github.com/jgvhabets

## Questions or contributions
Please don't hesitate to reach out if any questions or suggestions! @ juliette.vivien@charite.de  or https://twitter.com/vivien_juliette


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

