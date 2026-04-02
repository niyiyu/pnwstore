# Installation

The project is released to PyPI, so you can install it using the command below.
```bash
pip install pnwstore
```

If you want to install the latest development version, you can clone the repository and install it manually.

```bash
git clone https://github.com/Denolle/pnwstore.git pnwstore-dev
cd pnwstore-dev
pip install .
```

## mSEED Index Files
Make sure you have the mSEED sqlite index files. These sqlite index files are necessary for pnwstore to locate the file accurately and efficiently. Read the [backend/mseed.md](./backend/mseed.md) for more information on how to obtain these files.

## Pre-configured Machines
For Denolle group servers, pnwstore is already installed and configured. You can use the shared Python environment directly.
