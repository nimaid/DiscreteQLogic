#!/usr/bin/env python3

from pyeda.inter import *

class BooleanSimplifier:
    def _string_to_expr(string_in):
        return expr(string_in)
    
    def _simplify_expr(expr):
        simplified, = espresso_exprs(expr.to_dnf())
        return simplified
    
    def _expr_to_pos(expr):
        return expr.to_cnf()
    
    def simplify(string_in):
        orig_expression = BooleanSimplifier._string_to_expr(string_in)
        simp_expression = BooleanSimplifier._simplify_expr(orig_expression)
        pos_expression = BooleanSimplifier._expr_to_pos(simp_expression)
        print("~~~~~~~~ Simplified Expression (SoP) ~~~~~~~~\n")
        print(simp_expression)
        print("\n\n~~~~~~~~ PoS Expression ~~~~~~~~\n")
        print(pos_expression)