+++
date = "2025-05-12T11:18:34-05:00"
title = "Rust: personal reference"
draft = false
categories = ["reference"]
tags = ["rust"]
+++

## Methods on built-ins

### Hashmap

- `.entry` &mdash; Used for in-place manipulation of the value for a corresponding key, `scores.entry(team_id)`
- `.or_default` &mdash; Insert an empty default value if the key is not present, returning a mutable reference, `scores.entry(team_id).or_default()`
- `.or_insert` &mdash; Insert a populated default value if the key is not present, also returning a mutable reference, `sat_scores.entry(student_id).or_insert(400)`

### String slice

- `.len` &mdash; Get the length of the string slice, `name.len()`
- `.is_empty` &mdash; Check if the string slice is empty, `name.is_empty()`
- `.to_string` &mdash; Convert a string slice to a `String`, `name.to_string()`; compare, contrast with `String::from`

## Keywords

### Variable Bindings and Data Declaration

- `let` &mdash; Declare a variable
- `const` &mdash; Declare a compile-time constant
- `static` &mdash; Declare a static variable (global variable with a fixed memory location)
- `mut` &mdash; Mark a binding as mutable
- `ref` &mdash; Bind by reference

### Type System

- `type` &mdash; Create a type alias
- `struct` &mdash; Define a structure/record type
- `enum` &mdash; Define an enumeration type
- `trait` &mdash; Define an interface type
- `impl` &mdash; Implement methods or traits
- `dyn` &mdash; Dynamic dispatch to a trait object
- `Self` &mdash; Type alias for the implementing type within a trait or `impl`
- `self` &mdash; Method receiver or current module
- `super` &mdash; Parent module
- `where` &mdash; Add constraints to generic types

### Control Flow

- `if` &mdash; Conditional branching
- `else` &mdash; Alternative branch in conditional
- `match` &mdash; Pattern matching
- `loop` &mdash; Infinite loop
- `while` &mdash; Conditional loop
- `for` &mdash; Iterator-based loop
- `in` &mdash; Part of for loop syntax and pattern matching
- `break` &mdash; Exit a loop early
- `continue` &mdash; Skip to the next loop iteration
- `return` &mdash; Return from a function

### Functions and Closures

- `fn` &mdash; Define a function
- `move` &mdash; Force closure to take ownership of captured variables
- `async` &mdash; Define an asynchronous function or block
- `await` &mdash; Suspend execution until an async result is ready

### Memory Management

- `unsafe` &mdash; Denote unsafe code block
- `extern` &mdash; Link to external functions or crates
- `raw` &mdash; Raw pointer operations (used with references)

### Modules and Visibility

- `mod` &mdash; Define a module
- `pub` &mdash; Make an item public
- `use` &mdash; Import items from other modules
- `crate` &mdash; Reference the current crate or external crate
- `as` &mdash; Rename or alias in imports

### Macros

- `macro_rules`! &mdash; Define a declarative macro

### Type Operations

- `as` &mdash; Type casting
- `_` &mdash; Wildcard pattern or type placeholder

### Reserved for Future Use (No Functionality Yet)

- `abstract`
- `become`
- `box`
- `do`
- `final`
- `macro`
- `override`
- `priv`
- `try`
- `typeof`
- `unsized`
- `virtual`
- `yield`
