# Supercomputer-CO2

Quick, down-and-dirty Python file to determine how much CO2 your simulations have generated, as well as a print-out of your CPU time.

## How to use

Simply place all your slurm outputs (on IRIDIS5, ```slurm-*```) into a folder. Execute

```
python estimate_co2.py
```

and follow the on-screen instructions.

If you'd like to edit the wattage per CPU, edit the global varables defined in ALL_CAPS at the top of the script.

## Requirements

To install the requirements, do

```
pip install -r requirements.txt
```

Otherwise, you'll need ```tqdm``` and ```glob```.

## Tips n' Tricks


### Find and zip all your ```slurms``` at once
Want to zip up all your slurm files to download in one big go, and don't fancy manually going through your folders? Simply run:
```
find . -name "slurm-*" | zip my_file.zip -@
```
from the top level directory. Got some stuff in /scratch, or some other hard drive? You can update the above easily:
```
find /other_hdd/ -name "slurm-*" | zip -u existing_zip.zip -@
```

### Unzipping created loads of folders?
No problem! Just give a cheeky
```
mv **/slurm-* .
```
to move all your inflated files to this directory.


## Example output

```
Enter path to slurm files [Enter for ./]:
100%|████████████████████████████████████████| 751/751 [00:03<00:00, 194.11it/s]
Unfortunately, 17 files could not be decoded.
You have used 1881606138 seconds of CPU time. This is  522668.37 hours, or  21777.85 days, or  59.62 years of continuous computation time.
Your carbon footprint is therefore 40.19 tonnes!
```
