Title: [Note] 你所不知道的 C 語言：指標篇
Date: 2019-02-13 13:56
Tags: C, 你所不知道的 C 語言
Author: Naetw
Summary: 最近有空開始看 C 語言講座系列的直播，此系列主要記下 Jserv 在直播中提過但沒有細講的或是自己有興趣的內容。

> 最近有空開始看 C 語言講座系列的直播，此系列主要記下 Jserv 在直播中提過但是沒有細講或是自己有興趣的內容。其餘內容請參閱下方共筆連結。
>
> [原始課程共筆連結](https://hackmd.io/s/HyBPr9WGl)


# Declaration 的解讀

## 小小頭腦體操

取自 [C Traps and Pitfalls](http://www.literateprogramming.com/ctraps.pdf) 的案例 "Understanding Declarations"。

```c
(* (void(*)()) 0)();
```

要理解上述的 statement，個人認為需要對執行程式的背後機制有個簡單的認識：

首先程式（狹義上可說可執行檔）是一個靜態的概念，是由一些指令（機器碼 machine code）以及資料所組成的檔案（machine code 其實也是資料，不過會被放在被標記為可執行的區塊中），要執行程式會需要將程式載入至記憶體中，再由 CPU 去抓取指令來執行，這個抓取的動作便需要有指令所在位置的資訊。以一個簡單的程式為例：

```c
#include <stdio.h>

void func(void) {
    puts("Hello World");
}

int main(void) {
    func();
    return 0;
}
```

在 main 中呼叫了 `func()` 這個函式，代表著此時 CPU 要去存放 `func()` 的指令的位址來讀機器碼，在 CPU 中有個 Program Counter（又稱 Instruction Pointer）的暫存器用來記錄此時執行到哪條指令，也就是該暫存器是儲存一個位址，而該位址所存放的資料便是機器碼。

可以用 [GNU Bintuils](https://www.gnu.org/software/binutils/) 中的 `objdump` 來觀察，對可執行檔下以下指令：`objdump -d -M intel <your executable file>` 便可以觀察到如下資訊

```text
$ objdump -d -M intel a.out
...

Disassembly of section .text:

0000000100000f40 <_func>:
   100000f40:   55                      push   rbp
   100000f41:   48 89 e5                mov    rbp,rsp
   100000f44:   48 83 ec 10             sub    rsp,0x10
   ...

0000000100000f60 <_main>:
   100000f60:   55                      push   rbp
   100000f61:   48 89 e5                mov    rbp,rsp
   100000f64:   48 83 ec 10             sub    rsp,0x10
   100000f68:   c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0
   100000f6f:   e8 cc ff ff ff          call   100000f40 <_func>
   ...
```

看到最下面的 `call 100000f40` 那行便是告訴 CPU 要到 `0x100000f40` 的位址去抓指令（\*實際上 `call` 並非單純跳轉到其他地方去執行，它會儲存 return address 來幫助函式執行完可以回到原來的位置接下去執行\*），而該位址所存的資料是 `0x554889e54883ec10`，這些資料經過解讀後就是上面可以看到的 `push rbp` ... 等等指令。

現在再回來看上面那個頭腦體操：

```c
(* (void(*)()) 0)();
```

有了上面對函式呼叫的小認識，這裡的解讀應該就會輕鬆一些了：這個陳述式（statement）把 `0` 這個位址視作（轉型為）a pointer to a function returning void（也就是 `0` 是指標物件本身的位址，而在這位址上的資料是函式的位址），接著再用 indirection operator (`*`) 將它 dereference 為 function designator 來做函式呼叫。呼叫後會得到常見的 segmentation fault，這是因為 `0` 在大多數的作業系統中是被放在保留區 (reserved) 也就是不允許存取的區域。

實際上根據規格書，代表函式呼叫的運算式（expression）通常都是由 function designator 轉換而來 [1]，型別是 “pointer to a function returning type”，因此上面使用 `*` 基本上是沒有意義的，因為它將 a pointer to a function returning void 轉換成 a function returning void，但是在最後又會被轉換成 a pointer to a function returning void [2]。

[1]: C11 [6.5.2.2](http://port70.net/~nsz/c/c11/n1570.html#6.5.2.2) p1


- The expression that denotes the called function (Most often, this is the result of converting an identifier that is a function designator.) shall have type pointer to function returning void or returning a complete object type other than an array type.

[2]: C11 [6.3.2.1](http://port70.net/~nsz/c/c11/n1570.html#6.3.2.1) p4


- A function designator is an expression that has function type. Except when it is the operand of the sizeof operator, the _Alignof operator, or the unary & operator, a function designator with type ''function returning type'' is converted to an expression that has type ''pointer to function returning type''.
- 除了作為 `sizeof`, `_Alignof`, `&` 的運算元**以外**，function designator 都會被轉換成 “pointer to function returning type”

用一個極端的例子來看：


```c
#include <stdio.h>

void func(void) {
    printf("aaa\n");
}
int main(void) {
    void (*fptr)() = func;
    (**********fptr)();     // equivalent to fptr();
    (**********func)();     // equivalent to func();
    return 0;
}
```

最接近識別字（identifier）的 `*` 會將該識別字轉換成 function designator，但是透過上面的 [2] 它又會被轉換成 “pointer to function returning type”，第二個 `*` 又會轉換成 function designator … 以此類推，因此基本上不管放多少個 `*` 運算子，最終被解讀的型別仍舊會是 “pointer to function returning type”。

## Clockwise/Spiral Rule

函式 / 變數的宣告百百種，這裡介紹一個讓程式設計師可以人工分析 C 的宣告的規則。

> [The ``Clockwise/Spiral Rule'’](http://c-faq.com/decl/spiral.anderson.html) 的筆記
> 
> Copyright © 1993,1994 David Anderson
> This article may be freely distributed as long as the author's name and this notice are retained.

三個步驟：

1. 從想知道的元素開始（變數名稱、函式名稱），以順時針方向開始解讀，每遇到一個新的元素就加入該元素的描述。
    1. [X] or [] => Array X size of … or Array undefined size of
    2. (type1, type2) => function passing type1 and type2 returning …
    3. \* => pointer to …
2. 持續以順時針方向做 1. 的動作，直到所有語彙單位（tokens）都被解讀完畢
3. 括號（parenthesis）內的優先解讀

範例 1


```c
char *str[10];
```

想知道 `str` 是什麼，於是從它開始：


```c
      str
      str[10];   // str is an array 10 of ...
     *str        // str is an array 10 of pointers to ...
char *str[10];   // str is an array 10 of pointers to char
```

範例 2


```c
void (*signal(int, void (*fp)(int)))(int);
```

想知道 signal 是什麼：


```c
       signal
       signal(int, ...                      // signal is a function passing 
                                            // an int and a ...
                        (*fp)               // fp is a pointer to ...
                        (*fp)(int)          // fp is a pointer to a function
                                            // passing an int returning ...
                   void (*fp)(int)          // fp is a pointer to a function
                                            // passing an int returning void
       signal(int, void (*fp)(int))         // signal is a function passing 
                                            // an int and a pointer to
                                            // a function passing an int
                                            // returning void returning ...
      *signal(int, void (*fp)(int))         // signal is a function passing 
                                            // an int and a pointer to
                                            // a function passing an int
                                            // returning void
                                            // returning a pointer to ...
      *signal(int, void (*fp)(int))         // signal is a function passing 
                                            // an int and a pointer to
                                            // a function passing an int
                                            // returning void
                                            // returning a pointer to ...
      *signal(int, void (*fp)(int))(int);   // signal is a function passing 
                                            // an int and a pointer to
                                            // a function passing an int
                                            // returning void
                                            // returning a pointer to a
                                            // function passing an int
                                            // returning ...
void (*signal(int, void (*fp)(int)))(int);  // signal is a function passing 
                                            // an int and a pointer to
                                            // a function passing an int
                                            // returning void
                                            // returning a pointer to a
                                            // function passing an int
                                            // returning void
```


- 首先碰到左括號，知道它是個函式，並嘗試解讀括號內的東西
    - signal is a function passing an int and a …
- 碰到了另一個想理解的識別符（identifier）fp，於是像是遞迴函式先行解讀。先碰到右括號，先把括號內的東西解讀，遇到了 `*`
    - fp is a pointer to …
- 接著是左括號
    - fp is a pointer to a function passing an int returning …
- 接著是 `void`
    - fp is a pointer to a function passing an int returning nothin (void)
- 完成了 fp 的解讀，回到 signal 的解讀，將目前有的資訊結合
    - signal is a function passing an int and a pointer to a function passing an int returning nothing (void) returning …
- 接著是 `*`
    - signal is a function passing an int and a pointer to a function passing an int returning nothing (void) returning a pointer to …
- 接著是左括號
    - signal is a function passing an int and a pointer to a function passing an int returning nothing (void) returning a pointer to a function passing an int returning …
- 最後是 `void`
    - signal is a function passing an int and a pointer to a function passing an int returning nothing (void) returning a pointer to a function passing an int returning nothing (void)

## Compound Literals

> 源自 stack overflow 上[這篇](https://stackoverflow.com/questions/14105645/is-it-possible-to-create-an-anonymous-initializer-in-c99/14105698#14105698)，覺得挺有趣的，自己也沒用過 compound literals，紀錄一下。

大意是有人想用 C 讓 struct 做到像是 class 繼承那樣的效果，而他想到利用建構函式的參數來控制回傳的 struct 是哪一個（裡面有 a, b, c 三種）。這種選擇很簡單，使用 enum 就可以做到，問題是不同的 struct 裡面的資料結構不太一樣，他想要用一種 “anonymous variable” 來建構適當的 struct。

回答中提到了 compound literals，它是個 [C99 引進的特性](https://en.wikipedia.org/wiki/C99#Design)，我們能夠利用 initializer list 來製造一個無名物件（物件代表有專屬空間來存放資料），這個 compound literal 的結果為 lvalue [1]，也就是該物件的空間位址。由 casting + initializer list 組成，語法為：


```
(complete object type / array of unknown size){ initializer list }
```

也就是說我們可以做到像這樣的事情：


```c
drawline(&(struct point){ .x = 1, .y = 1 },
         &(struct point){ .x = 3, .y = 4 });
```

[1]: C11 [6.5.2.5](http://port70.net/~nsz/c/c11/n1570.html#6.5.2.5) p4


- If the type name specifies an array of unknown size, the size is determined by the initializer list as specified in [6.7.9](http://port70.net/~nsz/c/c11/n1570.html#6.7.9), and the type of the compound literal is that of the completed array type. Otherwise (when the type name specifies an object type), the type of the compound literal is that specified by the type name. In either case, the result is an lvalue.


## Flexible Array Members

同樣也是 [C99 引進的特性](https://en.wikipedia.org/wiki/C99#Design)。在介紹以前，假設有個情境是需要紀錄會員名字的結構，最簡單的方法可能是：


```c
struct User {
    uint32_t id;
    char name[20];
};
```

但並非每個人都會剛好用滿 20 個字元，會造成浪費，於是第二種方法出現：


```c
struct User {
    uint32_t id;
    char *name;
};
```

但是這樣會需要多一次 `malloc` 呼叫，且記憶體分佈可能會有破碎的情形。

Flexible array members 這個新特性可以一次解決上述兩種方法的缺點，它具有以下限制：


- 在 `struct` 內宣告一個 incomplete array type (e.g., `char name[]`，size of name is flexible)。
- 這個成員（flexible array member）必須要放在最後。
- 除了 flexible array member 外，`struct` 必須擁有至少一個成員。

以上面的問題來舉例 flexible array member 常見用法：


```c
char input[40];
ssize_t len;
struct User *p;

len = read(0, input, 40); // assume that this read() succeeds
p = (struct User *)malloc(sizeof(struct User) + len);
// ...
free(p);
```

在這情況下，上面的 `p` 相當於宣告為（在某些情況下，這個等效關係會不成立，詳見下方設計問題）：


```c
struct User { uint32_t id; char name[len]; } *p;
```

如此一來，避免了分配額外空間外也防止了記憶體破碎的問題。

### 設計問題（以 C11 為準）

首先看一個有趣的問題，擁有 flexible array member 的 `struct` 的大小會是多少？


```c
struct User {
    uint32_t id;
    char name[];
};
```

根據 C11 規格書 [1]，`struct` 的大小計算是**將 flexible array member 視為不存在**，不過有個例外是：根據其他成員組成，編譯器可能會做 padding，而這個 padding 是\***能夠**\*跟 flexible array member 的空間重疊的。也就是說 `sizeof(User) >= offsetof(struct User, name)`，且上面提到的等效宣告也就可能會失效（兩種方式中 `name` 在 `struct` 中的 offset 可能會不同）。因此在存取 flexible array member 時注意不能夠直接使用 `sizeof`，需十分注意。


延伸閱讀

- 由於其他的限制（像是 structure  / union 型別的成員指派行為使得 padding 的空間會拿到非特定的資料 [2]），flexible array member 有些不合理的未定義行為，詳情可見相關[缺陷報告（Defeat Report）](http://www.open-std.org/jtc1/sc22/wg14/www/docs/n2159.pdf)，內容十分詳盡！
- 在 C99 引進此特性以前，可以用小技巧（array of length 1）來做到類似的事情，某些編譯器可以支援 array of length 0，可參考 [gcc 的介紹](https://gcc.gnu.org/onlinedocs/gcc/Zero-Length.html)。

[1]: C11 [6.7.2.1 p18](http://port70.net/~nsz/c/c11/n1570.html#6.7.2.1p18)

- In most situations, the flexible array member is ignored. In particular, the size of the structure is as if the flexible array member were omitted except that it may have more trailing padding than the omission would imply.

[2]: C11 [6.2.6.1 p6](http://port70.net/~nsz/c/c11/n1570.html#6.2.6.1p6)

- When a value is stored in an object of structure or union type, including in a member object, the bytes of the object representation that correspond to any padding bytes take unspecified values.

Trivial Stuff
---

### `func()` v.s. `func(void)` in C11

```c
// Declaration

void func1();      // obsolescent
void func2(void);
```

- `func1` 沒有定義原型。（C11 specifies this as "function with no parameter specification". See [6.7.6.3 p16](http://port70.net/~nsz/c/c11/n1570.html#6.7.6.3p16)）
- `func2` 定義一個原型，這原型明確表示沒有任何 parameters。

> [parameter v.s. argument](https://en.wikipedia.org/wiki/Parameter_(computer_programming)#Parameters_and_arguments)
>
> - parameter (formal parameter)：在函式內用來代表參數的符號。
> - argument (actual argument)：傳入函式中實際上的值。

延伸閱讀

- [func() vs func(void) in c99](https://stackoverflow.com/questions/41803937/func-vs-funcvoid-in-c99)
	- 在 stackoverflow 上對這議題的討論。
- [Difference between identifier list and parameter type list](https://stackoverflow.com/questions/18820751/identifier-list-vs-parameter-type-list-in-c)
	- K&R-style 的宣告方式。


## Reference

- [程式設計師的自我修養](https://bit.ly/2K1P282)
- [C11 規格書](http://port70.net/~nsz/c/c11/n1570.html#Contents)
- [Wiki of Flexible array number](https://en.wikipedia.org/wiki/Flexible_array_member#cite_note-3)
- [Is the offset of a flexible array member subject to change](https://stackoverflow.com/questions/29336835/is-the-offset-of-a-flexible-array-member-subject-to-change)
