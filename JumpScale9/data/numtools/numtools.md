
## text2val


```python
j.tools.numtools.text2val("0.1mEUR")
```

- value can be 10%,0.1,100,1m,1k  m=million
- USD/EUR/CH/EGP/GBP are also understood
- all gets translated to usd
- e.g.: 10%
- e.g.: 10EUR or 10 EUR (spaces are stripped)
- e.g.: 0.1mEUR or 0.1m EUR or 100k EUR or 100000 EUR

## currencies

see https://github.com/Jumpscale/lib9/blob/development/JumpScale9Lib/clients/currencylayer/currencies.md for more info

```
import pprint; pprint.pprint(j.tools.numtools.currencies)
```

there are unique id's for each currency, see above link

