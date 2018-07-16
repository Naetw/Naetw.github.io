Title: [Note] 你所不知道的 C 語言：開發工具和規格標準篇
Date: 2018-02-06 10:27
Tags: C, 你所不知道的 C 語言
Author: Naetw
Summary: 最近有空開始看 C 語言講座系列的直撥，這篇主要記下 Jserv 在直播中提過但沒有細講的內容。

> 最近有空開始看 C 語言講座系列的直播，這篇主要記下 Jserv 在直播中提過但是沒有細講的內容。其餘內容請參閱下方共筆連結。
>
> [原始課程共筆連結](https://hackmd.io/s/HJFyt37Mx)

Designated Initializer
---

在 C90 時，初始化的順序必須要照著宣告時的順序，在 C99 後可以任意指定 member 來初始化

```c
int a[6] = { [4] = 29, [2] = 15 };
// is equivalent to
int a[6] = { 0, 0, 15, 0, 29, 0 };

struct point {
  int x, y;
};

// ====================================

struct point p = { .y = yvalue, .x = xvalue };
// is equivalent to
struct point p = { xvalue, yvalue };

// ====================================

/*
 * 沒有特別寫 designator 的初始值會給下一個接續的元素直接使用
 */
int a[6] = { [1] = v1, v2, [4] = v4 };
// is equivalent to
int a[6] = { 0, v1, v2, 0, v4, 0 };
```

- 在 `struct` 的 initialization 中，Omitted field members are implicitly initialized the same as objects that have static storage duration. (也就是會被初始化成跟 static variable 相同的值）
- *[index]*, *.fieldname* 被稱作 designator
    - 這兩個 designator 也可以同時使用
        - E.g., `struct` array 的初始化
            - `struct point ptarray[10] = { [2].y = yv2, [2].x = xv2, [0].x = xv0 };`
- `union` 的初始化方式跟 `struct` 一樣

> 註：在 GNU C++ 中並沒有上面這些規範，因此不能這樣使用。

Bootstrapping Compiler
---

意指一個透過自身語言來撰寫自身的 compiler。

Initial core 會是由別的語言撰寫通常是組合語言，而這個 core 會是該語言的一個很小的子集，接著會開始擴展，類似 0 生 1，1 生 2 ... 最後就成為一個 self-compiling compiler。

> 科普：bootstrapping 有「自助」、「不求人」之意，源自 19th-centry 某篇小說主角 "pull himself over a fence by his bootstraps"。
>
> 延伸閱讀：[第一個 C 语言编译器是怎样编写的？](http://blog.jobbole.com/94311/)

Lvalues
---

*lvalue* 原先真的是跟一個 assignment 的左側有關，但是後來較精準的定義是作為 "locator value" [1]，也就是說 *lvalue* 是一個物件的表示式 (an expression referring to an object)，這個物件的型態可以是一般的 object type or incomplete type，但是不可為 `void`。

- Object in C - 一種資料表示法
    - 原文：region of data storage in the execution environment, the contents of which can represent values
    - 在執行期間資料儲存的區域，可以表示數值的內容

[1]: The name "lvalue" comes originally from the assignment expression E1 = E2, in which the left operand E1 is required to be a (modifiable) lvalue. It is perhaps better considered as representing an object "locator value". What is sometimes called "rvalue" is in this International Standard described as the "value of an expression". An obvious example of an lvalue is an identifier of an object. As a further example, if E is a unary expression that is a pointer to an object, *E is an lvalue that designates the object to which E points. (C99 6.3.2.1 footnote)

一個簡單的例子：

```c
int a = 10;
int *E = &a;
++(*E);  // a = a + 1
++(a++); // error
```

- E 就是上面 [1] 所提及的 a pointer to an object (這裡的 object 指的就是 a 的 address)，下面列舉 E 這個 identifier 不同角度所代表的身份：
    - `E`
        - object: 儲存 address of int object 的區域
        - lvalue: E object 的位置，也就是 E object 這塊區域的 address
    - `*E`
        - lvalue: 對 E 這個 object 做 dereference 也就是把 E object 所代表的內容 (address of int object) 做 dereference，也就得到了 int object 的位置，換個說法就是上面 [1] 所提到的 lvalue that designates the object which E points。
- 在 gcc 7.2.1 中會產生 error: lvalue required as increment operand，因為 a++ 會 return a 的 value，而這個 value 是暫存值也就是一個 non-lvalue，而 ++() 這個 operator 的 operand 必須要是一個 lvalue，因為要寫回 data，需要有地方 (location) 可以寫。

> 注意：在 C 中只有分為 lvalue 跟 non-lvalue，rvalue 是在 C++ 中才被定義。

6.5.3.2 Address and indirection operators
---

- `&` 所能操作的 operand 只能是：
    - function designator - 基本上就是 function name
    - `[]` or `*` 的操作結果
        - 跟這兩個作用時，基本上就是相消
            - `*` - operand 本身
            - `[]` - `&` 會消失，而 `[]` 會被轉換成只剩 `+` (註：原本 `[]` 會是 `+` 搭配 `*`)
                - E.g., `&(a[5]) == a + 5`
    - 一個指向非 bit-field or register storage-class specifier 的 object 的 lvalue
        - bit-field：一種在 `struct` 或 `union` 中使用用來節省記憶體空間的 object
            - 特別的用途：沒有名稱的 bit-field 可以做為 padding
            - [Geeksforgeeks 上對 bit-field 的介紹](https://www.geeksforgeeks.org/bit-fields-c/)
- 除了遇到 `[]` 或 `*` 外，使用 `&` 的結果基本上都是得到 pointer to the object 或是 function 的 address
- `char str[123]`: why `str == &str`?
    - 實際上左右兩邊的型態是不一樣的，只是值相同。
        - 左邊的是 pointer to char：`char *`
            - 規格書中表示：除非遇到 `sizeof` 或是 `&` 之外，array of type (在這就是指 `str`) 都會被直接解讀成 pointer to type (在這就是 pointer to char)，而這個 type 是根據 array 的第一個元素來的 [1]
        - 右邊的則是 pointer to an array： `char (*)[123]`
            - 上面提到：遇到 `&` 時，`str` 不會被解讀為 pointer to type，而是做為原本的 object，在這就是 array object，而 address of array object 也就是這個 array object 的起始位址，當然也就會跟第一個元素的位址相同
    - 除了用值相同來解釋外，規格書在提到 equality operators 時，也有說到類似情境 [2]

[1]: Except when it is the operand of the sizeof operator or the unary & operator, or is a string literal used to initialize an array, an expression that has type ‘‘array of type’’ is converted to an expression with type ‘‘pointer to type’’ that points to the initial element of the array object and is not an lvalue. (C99 6.3.2.1)

[2]: Two pointers compare equal if and only if both are null pointers, both are pointers to the same object (including a pointer to an object and a subobject at its beginning) or function (C99 6.5.9)

好用的工具
---
- 英文很重要：`cdecl`：
    - 可以產生 C 語言的宣告，給英文回傳 C 語言，給 C 語言回傳英文。
- GDB
    - 神奇的工具 [rr](http://rr-project.org) (Record and Replay Framework)

Reference
---

- [Designated Initializer](https://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html)
- [Bootstrapping Compiler](https://en.wikipedia.org/wiki/Bootstrapping_(compilers))
- [<C/C++\> 左值和右值, L-value和R-value](http://www.cnblogs.com/dejavu/archive/2012/09/02/2667640.html)
- [C99 White Paper](http://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf)

