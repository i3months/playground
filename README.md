

```bash
./setup_rpi_injector.sh
sudo sysctl -w kernel.perf_event_paranoid=-1

make all

python3 collect_normal.py basicmath
python3 collect_marvin_style.py basicmath

cd visualize
python3 visualize_marvin.py basicmath
```

---

```bash
python3 collect_normal.py basicmath
```
```bash
python3 collect_marvin_style.py basicmath
```
```bash
python3 collect_fault.py
```
```bash
python3 collect_native_fault.py basicmath
```

```bash
python3 collect_normal.py basicmath       
python3 collect_marvin_style.py basicmath

python3 collect_normal.py qsort           
python3 collect_marvin_style.py qsort

python3 collect_normal.py sha             
python3 collect_marvin_style.py sha

python3 collect_normal.py target          
python3 collect_marvin_style.py target
```


