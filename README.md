# Cost of Disease
This repository contains the data and code for the analyses by [Jason DeBacker](https://jasondebacker.com/) ([@jdebacker](https://github.com/jdebacker/)), [Richard W. Evans](https://sites.google.com/site/rickecon) ([@rickecon](https://github.com/RickEcon/)), and Marcelo T. LaFleur ([SeaCelo](https://github.com/SeaCelo/)) in the article "The Economic Costs of a Resurgence of Disease in South Africa".

## How to run OG-ZAF macroecononomic simulations from the paper
We have a Python script in the [`/code/`](code/) directory of this repository called [`main.py`](code/main.py). Executing this `main.py` script in Python will run our baseline simulation of the model followed by our three spending cut and excess deaths scenarios. The underlying macroeconomic model is the open source [OG-ZAF](https://eapd-drb.github.io/OG-ZAF) overlapping generations macroeconomic model. The documentation for the OG-ZAF model is available online at https://eapd-drb.github.io/OG-ZAF and the documentation for the underlying OG-Core dependency of the model is also online at https://github.com/PSLmodels/OG-Core.

1. Make sure you have the Anaconda distribution of Python installed on your computer
    * Go to Ana
2. Either download or clone the `OG-ZAF` repository (the code for the macroeconomic model) to your local computer
    * To download the repository to your machine:
    * To clone the repository to your machine:
        * In your internet browser, navigate to the address of the `OG-ZAF` GitHub repository https://github.com/EAPD-DRB/OG-ZAF/.
3. Create the conda environment `ogzaf-dev` for the `OG-ZAF` model
    * In your terminal

## Files and directories in the repository
* [`.gitignore`](.gitignore): A Git software hidden file that tells Git which files and directories in which to ignore changes in the version history.
* [`./code/`](code/): Directory in which all the code and output of the model is stored.
    * [`./code/CostOutput`](code/CostOutput): Directory in which all the parameters, equilibrium output, and plots and tables output from the baseline and three reform scenarios are stored.
* [`LICENSE`](LICENSE): Creative Commons open source license for this repository.
* [`README.md`](README.md): README file with instructions on the content of and how to use this repository.
* [`./writing/`](writing/): Directory in which all of the draft LaTeX files and image files are stored.
    * [`./writing/disease.bib`](writing/disease.bib): BibTeX bibliography file for LaTeX paper references.
    * [`./writing/main.pdf`](writing/main.pdf): PDF file of paper.
    * [`./writing/main.tex`](writing/main.tex): LaTeX file of paper.
    * [`./writing/tables_figures/`](writing/tables_figures/): Directory where all the image files for figures and LaTex table files for the tables are stored.
        * []():
