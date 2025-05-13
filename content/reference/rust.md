+++
date = "2025-05-12T11:18:34-05:00"
title = "Rust: personal reference"
draft = false
categories = ["reference"]
tags = ["rust"]
+++

## Keywords

### Variable Bindings and Data Declaration

- `let` - Declare a variable
- `const` - Declare a compile-time constant
- `static` - Declare a static variable (global variable with a fixed memory location)
- `mut` - Mark a binding as mutable
- `ref` - Bind by reference

### Type System

- `type` - Create a type alias
- `struct` - Define a structure/record type
- `enum` - Define an enumeration type
- `trait` - Define an interface type
- `impl` - Implement methods or traits
- `dyn` - Dynamic dispatch to a trait object
- `Self` - Type alias for the implementing type within a trait or - impl
- `self` - Method receiver or current module
- `super` - Parent module
- `where` - Add constraints to generic types

### Control Flow

- `if` - Conditional branching
- `else` - Alternative branch in conditional
- `match` - Pattern matching
- `loop` - Infinite loop
- `while` - Conditional loop
- `for` - Iterator-based loop
- `in` - Part of for loop syntax and pattern matching
- `break` - Exit a loop early
- `continue` - Skip to the next loop iteration
- `return` - Return from a function

### Functions and Closures

- `fn` - Define a function
- `move` - Force closure to take ownership of captured variables
- `async` - Define an asynchronous function or block
- `await` - Suspend execution until an async result is ready

### Memory Management

- `unsafe` - Denote unsafe code block
- `extern` - Link to external functions or crates
- `raw` - Raw pointer operations (used with references)

### Modules and Visibility

- `mod` - Define a module
- `pub` - Make an item public
- `use` - Import items from other modules
- `crate` - Reference the current crate or external crate
- `as` - Rename or alias in imports

### Macros

- `macro_rules`! - Define a declarative macro

### Type Operations

- `as` - Type casting
- `_` - Wildcard pattern or type placeholder

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
