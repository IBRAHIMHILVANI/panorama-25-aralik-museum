"""Convert selected unmodified HEIC originals into portable FBX texture files."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25'
PREVIEW=ROOT/'review/walkthrough/textures'
PREVIEW.mkdir(parents=True,exist_ok=True)
selected=[1935,1936,1940,1941,1946,1949,1950,1951,1952,1955,1958,1960,1962,1963,1969,1973,1976,1978,1981,1982,1987,1994,1998,2001,2008,2011,2012,2015,2021,2022,2023,2024,2025,2026,2027,2033,2034,2041,2042,2045,2047,2048,2049,2050,2051,2052,2053,2055,2056,2057,2058,2061,2067,2068,2070,2072,2074,2076,2078,2081,2083,2085,2087,2096,2097,2102,2103,2107,2108,2114,2115,2122,2123,2128,2129,2132,2138,2141,2144,2148,2149,2150,2154,2157,2158,2165,2166,2167,2168,2170,2173,2176,2179,2187,2188,2193,2194,2196,2198,2200,2201,2205,2208,2211,2214,2217,2222,2225,2231,2237,2244,2249,2250,2253,2254,2255,2256,2257,2258]

def convert(n):
    source=ROOT/'drive-download-20261025T105004Z-1-001'/f'IMG_{n}.HEIC'
    dst=OUT/'textures'/f'IMG_{n}.jpg'
    if not dst.exists():
        subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','92','-Z','4096' if n>=2253 or n==1969 else '2560',str(source),'--out',str(dst)],capture_output=True,check=True)
    small=PREVIEW/dst.name
    if not small.exists():
        subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','85','-Z','2048' if n>=2253 or n==1969 else '1024',str(source),'--out',str(small)],capture_output=True,check=True)
    return {'id':n,'source':str(source.relative_to(ROOT)),'texture':str(dst.relative_to(OUT)),'operation':'format conversion and size limit only; original image content preserved'}

with ThreadPoolExecutor(max_workers=4) as pool:
    rows=[]
    for i,row in enumerate(pool.map(convert,selected)):
        rows.append(row)
        if (i+1)%25==0:print(f'Textures {i+1}/{len(selected)}',flush=True)
(OUT/'texture-provenance.json').write_text(json.dumps(rows,indent=2))
print('Prepared',len(rows),'photo textures',flush=True)
