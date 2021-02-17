# Install MiniConda
Linux https://conda.io/projects/conda/en/latest/user-guide/install/linux.html<br/>
MacOS https://conda.io/projects/conda/en/latest/user-guide/install/macos.html

# Install Dependencies
conda config --append channels conda-forge <br/>
conda create --name iridium python=3.7 <br/>
conda activate iridium <br/>
conda install -c conda-forge pytables <br/>
conda install pandas <br/>
conda install -c conda-forge jupyterlab

# Dependencies
https://github.com/mrjbq7/ta-lib

# PyPI
Go to project root directory <br/>
pip install -r etc/requirements.txt <br/>
pip install --editable . <br/>

*-e, --editable <path/url>   Install a project in editable mode (i.e. setuptools "develop mode")
                              from a local project path or a VCS url.*
                              
# Plot
pip install --upgrade mplfinance

# Documentation Development
pip install -r etc/requirements_docs.txt <br/>
cd docs <br/>
make html

# Jupyter Notebook
jupyter-lab

# Development
pip install -r etc/requirements_dev.txt <br/>

# Unit Testing
pytest --cov=iridium tests/

# Different Platforms
Mac:<br/>
brew install gcc <br/>
xcode-select --install   

# Sample call
iridium data -t f78990252f4a41e03fcbcb5f6cd80da5-06c80ae3156be464806b5a18e6077359 -s 2021-1-1 -i AUD_CAD -i AUD_CHF -i AUD_JPY -i AUD_NZD -i AUD_SGD -i AUD_USD -i CAD_CHF -i CAD_JPY -i CAD_SGD -i CHF_JPY -i EUR_AUD -i EUR_CAD -i EUR_CHF -i EUR_GBP -i EUR_JPY -i EUR_NZD -i EUR_SGD -i EUR_USD -i GBP_AUD -i GBP_CAD -i GBP_CHF -i GBP_JPY -i GBP_NZD -i GBP_SGD -i GBP_USD -i NZD_CAD -i NZD_CHF -i NZD_JPY -i NZD_SGD -i NZD_USD -i SGD_CHF -i SGD_JPY -i USD_CAD -i USD_CHF -i USD_JPY -i USD_SGD  --tz Australia/Sydney  --data-frequency M1