# Cost of Disease
This repository contains the data and code for the analyses by [Jason DeBacker](https://jasondebacker.com/) ([@jdebacker](https://github.com/jdebacker/)), [Richard W. Evans](https://sites.google.com/site/rickecon) ([@rickecon](https://github.com/RickEcon/)), and Marcelo T. LaFleur ([SeaCelo](https://github.com/SeaCelo/)) in the article "The Economic Costs of a Resurgence of Disease in South Africa".

## How to run OG-ZAF macroecononomic simulations from the paper
We have a Python script in the [`/code/`](code/) directory of this repository called [`main.py`](code/main.py). Executing this `main.py` script in Python will run our baseline simulation of the model followed by our three spending cut and excess deaths scenarios. The underlying macroeconomic model is the open source [OG-ZAF](https://eapd-drb.github.io/OG-ZAF) overlapping generations macroeconomic model. The documentation for the OG-ZAF model is available online at https://eapd-drb.github.io/OG-ZAF and the documentation for the underlying OG-Core dependency of the model is also online at https://github.com/PSLmodels/OG-Core.

The following are the steps to fully replicating all of our analyses in the paper.

1. Make sure you have the Anaconda distribution of Python installed on your computer
    * Go to https://www.anaconda.com/download in your internet browser
    * Select "Skip registration" under the big green "Submit button" (this will allow you to download the Python distribution without giving your email)
    * Select the correct Python installer for your operating system and chip set
    * In the graphical installer, select all the default settings
2. Either download or clone the `CostOfDisease` repository to your local computer
    * Navigate to the `CostOfDisease` GitHub repository (https://github.com/OpenSourceEcon/CostOfDisease) in your internet browser
    * To download the repository to your machine:
        * Click on the bright green "Code" button in the upper-right side of the page.
        * Click on the "Download ZIP" option in the bottom of the Local tab.
        * Place the contents of the downloaded "CostOfDisease-main.zip" file in the location you want on your hard drive.
    * To clone the repository to your machine:
        * Make sure you have Git software installed on your computer
        * Make sure you have signed up for your own user account on GitHub.com. (Go to https://github.com, click "Sign up", and follow the instructions)
        * Fork the `CostOfDisease` GitHub repository.
            * Navigate to the `CostOfDisease` GitHub repository (https://github.com/OpenSourceEcon/CostOfDisease)
            * Click the "Fork" button in the upper-right portion of the screen.
            * Click "Create fork". This will create a copy of this repository on your GitHub account.
        * Clone the repository from your GitHub account.
            * Open your Terminal (Anaconda prompt on Windows)
            * Navigate to the directory in which you want to place the `CostOfDisease` repository
            * Clone the repository to your hard drive: `git clone https://github.com/[YourGitHubHandle]/CostOfDisease.git`
3. Create the conda environment `disease-dev` from the [`environment.yml`](code/environment.yml) file
    * Open your Terminal (Anaconda prompt on Windows)
    * Navigate to the CostOfDisease repository
    * Create the `disease-dev` conda environment : `conda env create -f code/environment.yml`
4. Run the baseline simulation
    * Open your Terminal (Anaconda prompt on Windows)
    * Navigate to the CostOfDisease repository
    * Activate your `disease-dev` conda environment: `conda activate disease-dev`
    * Run the `main.py` Python script: `python ./code/main.py`
    * All the output will be saved in the [`./code/CostOutput/`](code/CostOutput/) directory.

## Files and directories in the repository
* [`.gitignore`](.gitignore): A Git software hidden file that tells Git which files and directories in which to ignore changes in the version history.
* [`./code/`](code/): Directory in which all the code and output of the model is stored.
    * [`./code/CostOutput`](code/CostOutput): Directory in which all the parameters, equilibrium output, and plots and tables output from the baseline and three reform scenarios are stored.
    * [`./code/environment.yml`](code/environment.yml): Conda environment file.
* [`LICENSE`](LICENSE): Creative Commons open source license for this repository.
* [`README.md`](README.md): README file with instructions on the content of and how to use this repository.
* [`./writing/`](writing/): Directory in which all of the draft LaTeX files and image files are stored.
    * [`./writing/disease.bib`](writing/disease.bib): BibTeX bibliography file for LaTeX paper references.
    * [`./writing/main.pdf`](writing/main.pdf): PDF file of paper.
    * [`./writing/main.tex`](writing/main.tex): LaTeX file of paper.
    * [`./writing/tables_figures/`](writing/tables_figures/): Directory where all the image files for figures and LaTex table files for the tables are stored.
        * [`./writing/tables_figures/cumulative_excess_deaths.png`](writing/tables_figures/cumulative_excess_deaths.png): Image file for Figure 1.
        * [`./writing/tables_figures/mortality_rates.png`](writing/tables_figures/mortality_rates.png): Image file for Figure 2.
