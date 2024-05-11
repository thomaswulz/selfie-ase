#!/bin/sh

riscv64-unknown-elf-as asm-inc-one.s -o asm-inc-one.obj
riscv64-unknown-elf-as asm-inc-two.s -o asm-inc-two.obj

riscv64-unknown-elf-ld asm-inc-one.obj -o asm-inc-one
riscv64-unknown-elf-ld asm-inc-two.obj -o asm-inc-two