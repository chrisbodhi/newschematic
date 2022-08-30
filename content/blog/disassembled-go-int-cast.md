# Dissecting an Integer Cast in Go

In a recent issue of [Go Weekly](), there was a link to [Ben Boyter's blog post](https://boyter.org/posts/cost-of-integer-cast-in-go/) on using Go's benchmarking capabilities to determine how relatively expensive different casting functions are. Take a look at the post.

I was curious about how we could use Go assembly[1] to develop an intuition for how expensive these casting functions are. Rather than futzing with my environment to view the assembly, I went to godbolt.org, the compiler explorer, and started writing functions. To see the full output of my explorations, [visit this link](https://godbolt.org/z/sb1nsjeE8). I opted to use `amd64` because the assembler is so much more readable than the `x86`.

I started with writing an identity function that takes an `int` and returns it:

```go
func Id(x int) int {
    return x
}
```

There's a good bit of setup that happens:

```asm
        TEXT    main.Id(SB), NOSPLIT|ABIInternal, $0-8
        FUNCDATA        $0, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $1, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $5, main.Id.arginfo1(SB)
        FUNCDATA        $6, main.Id.argliveinfo(SB)
        PCDATA  $3, $1
```

and then, the important bit:

```asm
        RET
```

The function just returns the input.

What about a function that takes an `int` and returns an `int32`?

```go
func Int32(x int) int32 {
    return int32(x)
}
```


```asm
        TEXT    main.Int32(SB), NOSPLIT|ABIInternal, $0-8
        FUNCDATA        $0, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $1, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $5, main.Int32.arginfo1(SB)
        FUNCDATA        $6, main.Int32.argliveinfo(SB)
        PCDATA  $3, $1
```

and then, just as before:

```asm
        RET
```

Same deal with casting to `int16` and `int8`, and even with `uint32`!

```go
func Uint32(x int) uint32 {
    return uint32(x)
}
```

```asm
        TEXT    main.Uint32(SB), NOSPLIT|ABIInternal, $0-8
        FUNCDATA        $0, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $1, gclocals·g2BeySu+wFnoycgXfElmcg==(SB)
        FUNCDATA        $5, main.Uint32.arginfo1(SB)
        FUNCDATA        $6, main.Uint32.argliveinfo(SB)
        PCDATA  $3, $1
        RET
```

So far, we're seeing that the benchmarks that Boyter created align with what we see in the Go assembly. But, what about working with floats?

```go
func Float32(x int) float32 {
    return float32(x)
}
```

After the same type of setup as before, we see

```asm
        XORPS   X0, X0
        CVTSQ2SS        AX, X0
        RET
```

We're no longer just returning the input




[1] If you aren't familiar with it, Go assembly is the intermediate step between Go source code (which we write) and machine code (which the computer runs). Peep [the Go docs](https://go.dev/doc/asm) for more information about this.