# midi-set-class

This is a python implementation of the code from Agustín Martorell & Emilia Gómez's
[Contextual Set-Class Analysis](https://link.springer.com/chapter/10.1007%2F978-3-319-25931-4_4)
for MIDI data.

> Martorell A., Gómez E. (2016) Contextual Set-Class Analysis. In: Meredith D. (eds) Computational Music Analysis. Springer, Cham. https://doi.org/10.1007/978-3-319-25931-4_4

# Setup
It is recommended you set up a virtual environment for python, then follow the install.
For example:

```bash
conda create -n midi-set-class python=3.8
conda activate midi-set-class
```

Only tested using python 3.8.

## Python install

```bash
path_to_repo=/path/to/midi-set-class
git clone https://github.com/JamesOwers/midi-set-class.git ${path_to_repo}
pip install ${path_to_repo}
```
## Contributors
If you would like to contribute, please install in developer mode and use the dev option
when installing the package. Additionally, please run `pre-commit install` to
automatically run pre-commit hooks.

```bash
pip install -e ${path_to_repo}[dev]
pre-commit install
```
