## How to perform an lrose-core build and install using miniforge and mamba

Normally lrose-core is built using the system libraries installed with the OS.

This procedure allows you to perform the build using only
the packages installed via miniforge,
which is an open source derivative of conda-forge.

### 1. Install miniforge3

The miniforge distribution is available in GitHub at:

* [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge)

Go to the latest release, for example:

* [https://github.com/conda-forge/miniforge/releases/tag/24.9.0-0](https://github.com/conda-forge/miniforge/releases/tag/24.9.0-0)

and download the .sh file for your OS. For example, I downloaded:

```
  Miniforge3-Linux-x86_64.sh
```

Make is executable:

```
  chmod +x Miniforge3-Linux-x86_64.sh
```

and then run it:

```
  ./Miniforge3-Linux-x86_64.sh
```

Install in the default location which is:

```
  $HOME/miniforge3
```

### 2. Install required packages in ```miniforge```

Check out ```lrose-bootstrap```:

```
  git clone https://github.com/ncar/lrose-bootstrap
```

Run the script to install the packages required by ```lrose-core```:

```
  cd lrose-bootstrap/miniforge
  ./install_mamba_packages
```

### 3. Build using conda-build

conda-build will build lrose-code, using the recipe in the meta.yaml file.

```
  cd lrose-bootstrap/miniforge
  ~/miniforge3/bin/conda-build .
```

### 4. Install the package using the local build

conda-build will build lrose-code, using the recipe in the meta.yaml file.

```
   ~/miniforge3/bin/mamba install --use-local lrose-core
```

```lrose-core``` will be installed in:

* ```~/miniforge3/bin```
* ```~/miniforge3/lib```
* ```~/miniforge3/include```

