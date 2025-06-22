# Notes

## TODO

* make frequency to any sound on piano.
* sound in the same volume as input.
* use input audio to output.

## 長3度下の出し方

ある音から下に長3度下の音は、

```math
\frac{440\times 2^n\times 2^{-\frac{4}{12}}}{440\times2^n}=2^{-\frac{4}{12}}
```

倍だから、これをかけてやればいいはず。
