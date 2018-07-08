Title: Use snipmate in vim to make life easier
Date: 2017-01-04 09:09
Tags: vim
Author: Naetw
Summary: A note of using snipmate in vim

## Description

> 在打 CTF 的時候，每次解 pwn 都要重複打一些基本設定覺得很麻煩很懶，後來發現了 [snipmate](https://github.com/garbas/vim-snipmate) + [vim-snippets](https://github.com/honza/vim-snippets) 覺得滿好用的，很適合我這種懶人

## Install

個人是用 [Vundle](https://github.com/gmarik/vundle)，其他安裝方式可以到 GitHub 上去看

在 .vimrc 裡面的 `call vundle#begin()` 跟 `call vundle#end()` 之間加入以下幾行：

```
Plugin 'MarcWeber/vim-addon-mw-utils'
Plugin 'tomtom/tlib_vim'
Plugin 'garbas/vim-snipmate'
Plugin 'honza/vim-snippets'
```

snipmate depends on [vim-addon-mw-utils](https://github.com/marcweber/vim-addon-mw-utils) and [tlib_vim](https://github.com/tomtom/tlib_vim)，所以這兩個也要一併裝起來

而裝了 snipmate 後還沒有任何 snippets 可以用，所以也會裝 vim-snippets，這是 snipmate default snippets，這樣一來就可以支援各種語言

## Usage

平常打 CTF 解 pwn 題基本上都需要:

```python
#!/usr/bin/env python

from pwn import *

ip = '127.0.0.1'
port = 4000

r = remote(ip, port)
```

每次都要打一遍雖然很快但很麻煩@@，有了 snippets 可以很快的完成

只要在 `~/.vim/` 底下建一個 snippets directory，在裡面可以放不同語言的 snippets，以我的例子是建一個 `python.snippets`，在裡面加入以下幾行：

```
snippets pwn
    #!/usr/bin/env python

    from pwn import *

    ip = '127.0.0.1'
    port = 4000

    r = remote(ip, port)
```

這樣一來我只要輸入 pwn 之後按下 tab 就可以生出 snippets 裡面所記錄的 code

|                Demo                   |
|:-------------------------------------:|
|![Demo](http://i.imgur.com/jyNKSc6.gif)|
