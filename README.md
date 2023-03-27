

## How Does the Cache Work?
### Write-Back vs Write-Through Mode
In write-through mode, every time a value is written to a memory location stored in the cache, it is also written to 
the memory. In a write-back cache, data written to the cache is only written to the memory if that cache block is 
replaced. 