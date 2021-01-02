#!/usr/bin/env python


def tc(val, nbits):
    """Compute the 2's complement of int value val. Credit: https://stackoverflow.com/a/37075643/9235421"""
    if val < 0:
        if (val + 1).bit_length() >= nbits:
            raise ValueError(f"Value {val} is out of range of {nbits}-bit value.")
        val = (1 << nbits) + val
    else:
        if val.bit_length() > nbits:
            raise ValueError(f"Value {val} is out of range of {nbits}-bit value.")
        # If sign bit is set.
        if (val & (1 << (nbits - 1))) != 0:
            # compute negative value.
            val = val - (1 << nbits)
    return val
