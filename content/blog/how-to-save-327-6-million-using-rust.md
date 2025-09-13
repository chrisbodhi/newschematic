+++
date = "2025-09-09T17:33:27-05:00"
draft = false
categories = ["programming",]
tags = ["rust", "aerospace", "space",]
comments = false
showcomments = false
showpagemeta = true
title = "How to save $327.6 million using Rust"
+++

It was 1999. In my memory, I'm in Mr. Wilson's chemistry class when I hear about the cause of the crash, but I'm not sure about that. What I am sure about, though, is the feeling: overwhelm at the sheer magnitude of the blunder. $327.6 million spacecraft was lost in seconds. Three years of development. Ten months traveling through space. All because two teams used different units.

Could Rust have prevented this disaster?

## The Newtype Idiom

From [Rust by Example](https://doc.rust-lang.org/rust-by-example/types/structs/newtype.html):

>The `newtype` idiom gives compile time guarantees that the right type of value is supplied to a program.

This may seem obvious, or even redundant, as it's one of the primary reasons we enjoy typed languages. But what the idiom provides for us is a way to get even more specific about the units we're using. For example, we can define a newtype for meters:

```rust
struct Meters(f64);

impl Meters {
    fn new(meters: f64) -> Self {
        Meters(meters)
    }
}

fn main() {
    let distance = Meters::new(100.0);
    println!("Distance: {} meters", distance.0);
}
```

And what can ensure that a consuming function will only accept values of this type? Rust's type system!

```rust
fn calculate_area(radius: Meters) -> Meters {
    let area = std::f64::consts::PI * radius.0.powi(2);
    Meters(area)
}

fn calculate_volume(radius: Meters) -> Meters {
    let volume = std::f64::consts::PI * radius.0.powi(3);
    Meters(volume)
}
```

If accessing the underlying value with the `0` index gives you pause, you can define a method to access it:

```rust
impl Meters {
    fn value(&self) -> f64 {
        self.0
    }
}
```

Or even better yet, define methods to work with the value:

```rust
impl Meters {
    fn value(&self) -> f64 {
        self.0
    }

    fn add(&self, other: &Meters) -> Meters {
        Meters(self.0 + other.0)
    }

    fn subtract(&self, other: &Meters) -> Meters {
        Meters(self.0 - other.0)
    }

    fn powi(&self, exponent: i32) -> Meters {
        Meters(self.0.powi(exponent))
    }

    fn sqrt(&self) -> Meters {
        Meters(self.0.sqrt())
    }
}
```

>We'll hold off on adding support for common mathematical operators, like `+` and `-`, because this makes the point.

This looks like burdensome boilerplate. For some use cases, it is! But unit math rarely changes, making this perfect work for an LLM to generate along with tests and documentation.

## Seeing is believing

"But, wait," you say, "what about the runtime costs?" There are _no runtime costs_ with this approach. This is what is meant when folks in the Rust community say "Zero Cost Abstractions." The compiler removes the newtypes and then the hardware treats the values as `f64`, or whatever they're defined to use, when executing the code.

Weary about such a statement? I understand. So, take a look at these two examples in [Godbolt](https://godbolt.org/) to compare the generated assembly (Rust 1.89.0, with the `-O` flag set):

_With newtypes_

```rs
#[unsafe(no_mangle)]
pub fn main() -> Time {
    let mu = GravitationalParameter(398600.4418);
    let semi_major_axis = Distance(3.844e8);
    let period = orbital_period_typed(mu, semi_major_axis);

    period
}

struct GravitationalParameter(f64);
struct Distance(f64);
pub struct Time(f64);

#[unsafe(no_mangle)]
fn orbital_period_typed(mu: GravitationalParameter, a: Distance) -> Time {
    Time(2.0 * std::f64::consts::PI * (a.0.powi(3) / mu.0).sqrt())
}
```

```assembly
.LCPI0_0:
        .quad   0x4032c76af7b8cc96
main:
        movsd   xmm0, qword ptr [rip + .LCPI0_0]
        ret

.LCPI1_0:
        .quad   0x401921fb54442d18
orbital_period_typed:
        movapd  xmm2, xmm1
        mulsd   xmm2, xmm1
        mulsd   xmm2, xmm1
        divsd   xmm2, xmm0
        xorps   xmm0, xmm0
        sqrtsd  xmm0, xmm2
        mulsd   xmm0, qword ptr [rip + .LCPI1_0]
        ret
```

_Without newtypes_

```rs
#[unsafe(no_mangle)]
pub fn main() -> f64 {
    let mu = 398600.4418;
    let semi_major_axis = 3.844e8;
    let period = orbital_period_raw(mu, semi_major_axis);

    period
}

#[unsafe(no_mangle)]
fn orbital_period_raw(mu: f64, semi_major_axis: f64) -> f64 {
    2.0 * std::f64::consts::PI * (semi_major_axis.powi(3) / mu).sqrt()
}
```

```assembly
.LCPI0_0:
        .quad   0x4032c76af7b8cc96
main:
        movsd   xmm0, qword ptr [rip + .LCPI0_0]
        ret

.LCPI1_0:
        .quad   0x401921fb54442d18
orbital_period_raw:
        movapd  xmm2, xmm1
        mulsd   xmm2, xmm1
        mulsd   xmm2, xmm1
        divsd   xmm2, xmm0
        xorps   xmm0, xmm0
        sqrtsd  xmm0, xmm2
        mulsd   xmm0, qword ptr [rip + .LCPI1_0]
        ret
```

More directly, that diff looks like this:

![asm diff](/img/asm-diff.png)

## Ok, so now what?

Could Rust prevent a similar disaster? The newtype system makes unit mismatches much harder to introduce. But prevention isn't just about the language—it's about the conversations between teams and the processes around critical calculations.

Aerospace code is still largely Ada, C, and C++. The next technical question becomes: how do we bring this type safety to existing systems through interop while maintaining the expressiveness that prevents these costly mistakes?

* * *

Read more about the Mars Climate Orbiter on [Wikipedia](https://en.wikipedia.org/wiki/Mars_Climate_Orbiter).

_Thanks to Adam Melnyk for reviewing._
