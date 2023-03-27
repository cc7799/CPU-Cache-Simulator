# CPU Cache Simulator
Simulates writes to and reads from a single-level CPU cache.

This project was created as a project for the Computer Architecture (CS 3220) class I took while a student at UVM.

## Table of Contents
* [Description](#description)
* [Installation & Setup](#installation--setup)
* [Operation](#operation)
* [How Does the Cache Work?](#how-does-the-cache-work)

## Description
This program simulates reads and writes to a CPU cache. The address size, cache size, block size, and associativity are 
all able to be changed. Additionally, the cache can be run in write-back or write-through mode.

## Installation & Setup
No setup is required. All modules are from the Python standard library.

## Operation
The program is run by running the `main.py` module. A basic setup is provided, but can be changed by modifying the 
constants in `main.py`.

Each read or write operation will print the results of the operation to the console. Try messing around with the values 
and see what happens!

## How Does the Cache Work?
(This section is currently a WIP)
### Write-Back vs Write-Through Mode
In write-through mode, every time a value is written to a memory location stored in the cache, it is also written to 
the memory. In a write-back cache, data written to the cache is only written to the memory if that cache block is 
replaced. 